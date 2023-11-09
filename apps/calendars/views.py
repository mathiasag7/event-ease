import datetime as dt
import os
from pathlib import Path

from django.conf import settings
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.core.paginator import Paginator
from django.http import Http404, QueryDict
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from django_htmx.http import HttpResponseClientRedirect
from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar
from gcsa.recurrence import Recurrence
from render_block import render_block_to_string

from .forms import CalendarCreateEditForm
from .forms import CalendarSearchForm

CREDENTIALS_DIR = f"{settings.BASE_DIR}/.credentials"


def _connect():
    credentials_path = Path(f"{CREDENTIALS_DIR}/id_token.json")
    if credentials_path:
        return GoogleCalendar(credentials_path=credentials_path)
    else:
        # let the sdk dectect the credentials
        return GoogleCalendar()


def _disconnect() -> None:
    old_token = f"{CREDENTIALS_DIR}/token.pickle"
    if old_token and os.path.exists(old_token):
        os.remove(old_token)
    return None


def pagination(request: HttpRequest, objects, number: int = 16
               ) -> QueryDict:
    parm_copy: QueryDict = request.GET.copy()
    try:
        page_number = int(parm_copy.pop("page")[0])
    except KeyError:
        page_number = 1
    request.GET = parm_copy

    pages = Paginator(objects, number)

    try:
        events = pages.get_page(page_number)  # returns the desired page object
    except PageNotAnInteger:
        # if page_number is not an integer then assign the first page
        events = pages.page(1)
    except EmptyPage:
        # if page is empty then return last page
        events = pages.page(pages.num_pages)

    events.adjusted_elided_pages = pages.get_elided_page_range(page_number)
    return events


# TODO Rename this here and in `calendars`
def calendar_form_view(form, gc):
    _today = dt.datetime.now().date()
    search = form.cleaned_data.get("search", "")
    start = form.cleaned_data.get("start", None)
    end = form.cleaned_data.get("end", None)
    return gc.get_events(
        time_min=start,
        time_max=end,
        query=search,
        single_events=True,
        order_by="startTime",
    )


def list_event(request: HttpRequest) -> HttpResponse:
    gc = _connect()
    events = gc.get_events()
    form = CalendarSearchForm(request.GET)
    if form.is_valid():
        events = calendar_form_view(form, gc)
    events = list(events)
    objects = pagination(request, events)
    context = {"events": objects, "form": form}

    if request.headers.get("HX-Request"):
        return HttpResponse(
            render_block_to_string(
                "calendars/list.html", "events_result", context, request
            )
        )
    return TemplateResponse(request, "calendars/list.html", context)


def get_event(request: HttpRequest, event_id: str) -> HttpResponse:
    gc = _connect()
    try:
        event = gc.get_event(event_id)
    except Exception as e:
        raise Http404() from e
    return render(request, "calendars/details.html", {"event": event})


def create_recurrence(event, r_rule, r_data):
    if r_data is not None:
        recurrence = (
            []
            if r_rule in ("RDATE", "EXDATE")
            else [f"{r_rule}:{Recurrence._rule(**r_data)}"]
        )
        event.recurrence = recurrence
    return event


def create_event(request: HttpRequest) -> HttpResponse:
    form = CalendarCreateEditForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        event = Event(
            summary=form.cleaned_data.get("summary"),
            description=form.cleaned_data.get("description"),
            start=form.cleaned_data.get("start"),
            end=form.cleaned_data.get("end"),
            timezone=form.cleaned_data.get("timezone"),
            color_id=form.cleaned_data.get("color"),
        )
        event = create_recurrence(
            event,
            form.cleaned_data.get("recurrence_rule"),
            form.cleaned_data.get("recurrence"),
        )
        gc = _connect()
        gc.add_event(event)
        return redirect(reverse("calendars:list"))
    return TemplateResponse(
        request,
        "calendars/create_edit.html",
        {
            "form": form,
            "url": reverse("calendars:create"),
        },
    )


# TODO Rename this here and in `update_event`
def update_changed_event(form, event, gc):
    event.summary = form.cleaned_data.get("summary")
    event.description = form.cleaned_data.get("description")
    event.start = form.cleaned_data.get("start")
    event.end = form.cleaned_data.get("end")
    event.timezone = form.cleaned_data.get("timezone")
    event.color_id = form.cleaned_data.get("color")

    event = create_recurrence(
        event,
        form.cleaned_data.get("recurrence_rule"),
        form.cleaned_data.get("recurrence"),
    )
    gc = _connect()
    gc.update_event(event)
    return redirect(reverse("calendars:list"))


def update_event(request: HttpRequest, event_id: str) -> HttpResponse:
    gc = _connect()
    try:
        event = gc.get_event(event_id)
    except Exception as e:
        raise Http404() from e
    form = CalendarCreateEditForm(
        request.POST or None,
        initial={
            "id": event.id,
            "color": event.color_id,
            "summary": event.summary,
            "description": event.description,
            "start": event.start,
            "end": event.end,
        },
    )
    if request.method == "POST" and (form.is_valid() and form.has_changed()):
        return update_changed_event(form, event, gc)
    return TemplateResponse(
        request,
        "calendars/create_edit.html",
        {
            "form": form,
            "url": reverse("calendars:update", kwargs={"event_id": event_id}),
        },
    )


@require_POST
def delete_event(request: HttpRequest, event_id: str) -> HttpResponse:
    gc = _connect()
    try:
        gc.delete_event(event_id)
    except Exception as e:
        raise Http404() from e
    return HttpResponseClientRedirect(reverse("calendars:list"))


def switch_user(request: HttpRequest) -> HttpResponse:
    _disconnect()
    return redirect(reverse("calendars:list"))
