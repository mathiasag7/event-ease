import datetime as dt
import calendar
from random import choice
from typing import Any

from django import forms
from dynamic_forms import DynamicField
from dynamic_forms import DynamicFormMixin
from apps.calendars.recurrences import clean_recurrence
from apps.recurrence import forms as f


LAVENDER = (1, "LAVENDER")
SAGE = (2, "SAGE")
GRAPE = (3, "GRAPE")
FLAMINGO = (4, "FLAMINGO")
BANANA = (5, "BANANA")
TANGERINE = (6, "TANGERINE")
PEACOCK = (7, "PEACOCK")
GRAPHITE = (8, "GRAPHITE")
BLUEBERRY = (9, "BLUEBERRY")
BASIL = (10, "BASIL")
TOMATO = (11, "TOMATO")

COLOR_CHOICES = [
    LAVENDER,
    SAGE,
    GRAPE,
    FLAMINGO,
    BANANA,
    TANGERINE,
    PEACOCK,
    GRAPHITE,
    BLUEBERRY,
    BASIL,
    TOMATO,
]

COLOR_VALUES = {
    "LAVENDER": "#A4BDFC",
    "SAGE": "#7AE7BF",
    "GRAPE": "#DBADFF",
    "FLAMINGO": "#FF887C",
    "BANANA": "#FBD75B",
    "TANGERINE": "#FFB878",
    "PEACOCK": "#46D6DB",
    "GRAPHITE": "#E1E1E1",
    "BLUEBERRY": "#5484ED",
    "BASIL": "#51B749",
    "TOMATO": "#DC2127",
}


def _next_month(now):
    date = now + dt.timedelta(days=calendar.monthrange(now.year, now.month)[1])
    start = now.replace(day=1)
    end = now.replace(
        day=calendar.monthrange(now.year, now.month + 1)[1],
        month=now.month + 1 if now.month < 12 else 1,
        year=date.year if now.month < 12 else now.year + 1,
    )
    return start, end


class CalendarSearchForm(forms.Form):
    search = forms.CharField(
        label="Search",
        required=False,
    )
    start = forms.DateField(
        label="Start",
        required=False,
        widget=forms.DateInput(
            attrs={
                "type": "date",
            }
        ),
    )
    end = forms.DateField(
        label="End",
        required=False,
        widget=forms.DateInput(
            attrs={
                "type": "date",
            }
        ),
    )

    options = forms.ChoiceField(
        choices=[
            ("two_years", "2 years"),
            ("this_week", "This week"),
            ("next_week", "Next week"),
            ("this_month", "This month"),
            ("next_month", "Next month"),
            ("this_year", "This year"),
            ("next_year", "Next year"),
            ("five_years", "5 years"),
            ("ten_years", "10 years"),
        ],
        initial="all",
        label="Options",
        required=False,
    )

    def clean(self):
        now = dt.datetime.now().date()
        cleaned_data = super().clean()
        options = cleaned_data.get("options")
        start = cleaned_data.get("start")
        end = cleaned_data.get("end")
        search = cleaned_data.get("search")
        if start is None and end is None:
            print(options)
            if options == "two_year":
                start, end = now.replace(year=now.year, month=1, day=1), now.replace(
                    year=now.year + 2, month=12, day=31
                )
            elif options == "this_week":
                start = now - dt.timedelta(days=now.weekday())
                end = start + dt.timedelta(days=6)
            elif options == "next_week":
                start = now + dt.timedelta(days=7 - now.weekday())
                end = start + dt.timedelta(days=6)
            elif options == "this_month":
                start, end = now.replace(day=1), now.replace(
                    day=calendar.monthrange(now.year, now.month)[1]
                )
            elif options == "next_month":
                start, end = _next_month(now)
            elif options == "this_year":
                start, end = now.replace(month=1, day=1), now.replace(month=12, day=31)
            elif options == "next_year":
                start, end = now.replace(
                    year=now.year + 1, month=1, day=1
                ), now.replace(year=now.year + 1, month=12, day=31)
            elif options == "five_years":
                start, end = now.replace(year=now.year, month=1, day=1), now.replace(
                    year=now.year + 5, month=12, day=31
                )
            elif options == "ten_years":
                start, end = now.replace(year=now.year, month=1, day=1), now.replace(
                    year=now.year + 10, month=12, day=31
                )
            return {
                "search": search,
                "start": start,
                "end": end,
            }


class CalendarCreateEditForm(DynamicFormMixin, forms.Form):
    from django.urls import reverse_lazy

    summary = forms.CharField(
        label="Summary",
    )
    description = forms.CharField(label="Description", required=False)

    start = DynamicField(
        forms.DateTimeField,
        label="Start",
        required=False,
        widget=forms.DateTimeInput(
            attrs={
                "type": "datetime-local",
            }
        ),
    )
    end = DynamicField(
        forms.DateTimeField,
        label="End",
        required=False,
        widget=forms.DateTimeInput(
            attrs={
                "type": "datetime-local",
            }
        ),
    )
    recurrence = f.RecurrenceField(max_rrules=1, required=False)
    color = forms.ChoiceField(
        choices=COLOR_CHOICES,
        label="Color",
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start")
        end = cleaned_data.get("end")
        recurrence = cleaned_data.get("recurrence")
        data = {}
        if not start and not recurrence:
            raise forms.ValidationError("Start or recurrence is required.")
        elif start:
            if start < dt.datetime.now(tz=start.tzinfo):
                raise forms.ValidationError("Start must be in the future.")
            if end and start > end:
                raise forms.ValidationError("Start must be before end.")
            timezone = start.tzinfo
            data |= {
                "start": start,
                "end": end.astimezone(timezone) if end else None,
                "timezone": str(timezone),
            }

        if recurrence:
            recurrence = str(recurrence)
            recurrence_rule = clean_recurrence(recurrence)[0]
            recurrence_dict = clean_recurrence(recurrence)[1]
            data |= {"recurrence_rule": recurrence_rule, "recurrence": recurrence_dict}

        data |= {
            "summary": cleaned_data.get("summary"),
            "description": cleaned_data.get("description"),
            "color": str(cleaned_data.get("color")),
        }
        return data
