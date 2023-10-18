import datetime as dt
from django.http import Http404, HttpRequest, HttpResponse
from django.urls import reverse

from gcsa.google_calendar import GoogleCalendar
from gcsa.event import Event
from gcsa.recurrence import Recurrence
from django.shortcuts import redirect, render
from .forms import CalendarCreateEditForm, CalendarSearchForm
from django.core.paginator import Paginator
from django.template.response import TemplateResponse
from django.views.decorators.http import require_POST
from django_htmx.http import HttpResponseClientRedirect
from django.views.decorators.csrf import csrf_exempt


def _connect():
    return GoogleCalendar("testinfront7@gmail.com", credentials_path="/Users/ace/projects/dj_google_apis/.credentials/id_token.json") # type: ignore


def pagination(request: HttpRequest, objects, number: int = 10):
    paginator = Paginator(objects, number)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


# TODO Rename this here and in `calendars`
def calendar_form_view(form, gc):
    search = form.cleaned_data.get('search', "")
    start = form.cleaned_data.get('start', dt.datetime.now())
    end = form.cleaned_data.get('end', dt.datetime.now().replace(day=31, month=12))
    return gc.get_events(
        time_min=start,
        time_max=end,
        query=search,
        single_events=True,
        order_by="startTime",
    )


def list_event(request: HttpRequest) -> HttpResponse:
    gc = _connect()
    events = gc.get_events(time_min=dt.datetime.now(), time_max=dt.datetime.now().replace(day=31, month=12),)
    form = CalendarSearchForm(request.GET)
    if form.is_valid():
        events = calendar_form_view(form, gc)
    events = list(events)
    objects = pagination(request, events)
    return render(request, 'calendars/list.html', {'events': objects, "form": form})


def get_event(request: HttpRequest, event_id: str) -> HttpResponse:
    gc = _connect()
    try:
        event = gc.get_event(event_id)
    except Exception as e:
        raise Http404() from e
    return render(request, 'calendars/details.html', {'event': event})


def create_recurrence(event, r_rule, r_data):
    if r_data is not None:
        recurrence = (
            [f'{r_rule}:{Recurrence._times(**r_data)}']
            if r_rule in ("RDATE", "EXDATE")
            else [f'{r_rule}:{Recurrence._rule(**r_data)}']
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
        event = create_recurrence(event, form.cleaned_data.get("recurrence_rule"), form.cleaned_data.get("recurrence"))
        gc = _connect()
        gc.add_event(event)
        return redirect(reverse("calendars:list"))
    return TemplateResponse(request, "calendars/create_edit.html", {"form": form, "url": reverse("calendars:create"),})


# def recurrence(request: HttpRequest) -> HttpResponse:
#     form = CalendarCreateEditForm(initial=request.GET, context={"add_custom_recurrence": request.GET.get("add_custom_recurrence")})
#     return HttpResponse(as_crispy_form(form))


# TODO Rename this here and in `update_event`
def update_changed_event(form, event, gc):
    event.summary=form.cleaned_data.get("summary")
    event.description=form.cleaned_data.get("description")
    event.start=form.cleaned_data.get("start")
    event.end=form.cleaned_data.get("end")
    event.timezone=form.cleaned_data.get("timezone")
    event.color_id=form.cleaned_data.get("color")

    event = create_recurrence(event, form.cleaned_data.get("recurrence_rule"), form.cleaned_data.get("recurrence"))
    gc = _connect()
    gc.update_event(event)
    return redirect(reverse("calendars:list"))


def update_event(request: HttpRequest, event_id: str) -> HttpResponse:
    gc = _connect()
    try:
        event = gc.get_event(event_id)
    except Exception as e:
        raise Http404() from e
    form = CalendarCreateEditForm(request.POST or None, initial={"id": event.id, "color": event.color_id, "summary": event.summary, "description": event.description, "start": event.start, "end": event.end})
    if request.method == "POST" and (form.is_valid() and form.has_changed()):
        return update_changed_event(form, event, gc)
    return TemplateResponse(request, "calendars/create_edit.html", {"form": form, "url": reverse("calendars:update", kwargs={"event_id": event_id}),})





@require_POST
@csrf_exempt
def delete_event(request: HttpRequest, event_id: str) -> HttpResponse:
    gc = _connect()
    try:
        gc.delete_event(event_id)
    except Exception as e:
        raise Http404() from e
    return HttpResponseClientRedirect(reverse("calendars:list"))