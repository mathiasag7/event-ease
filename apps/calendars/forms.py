import datetime

from django import forms
from dynamic_forms import DynamicField
from dynamic_forms import DynamicFormMixin

from apps.calendars.recurrences import clean_recurrence


LAVENDER = (1, "#A4BDFC")
SAGE = (2, "#7AE7BF")
GRAPE = (3, "#DBADFF")
FLAMINGO = (4, "#FF887C")
BANANA = (5, "#FBD75B")
TANGERINE = (6, "#FFB878")
PEACOCK = (7, "#46D6DB")
GRAPHITE = (8, "#E1E1E1")
BLUEBERRY = (9, "#5484ED")
BASIL = (10, "#51B749")
TOMATO = (11, "#DC2127")

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

now = datetime.datetime.now()


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
        # initial=now,
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
        # initial=now + datetime.timedelta(days=1),
        widget=forms.DateTimeInput(
            attrs={
                "type": "datetime-local",
            }
        ),
    )
    recurrence = DynamicField(
        forms.CharField,
        label="Recurrence",
        required=False,
        widget=forms.Textarea(attrs={"class": "recurrence-widget"}),
    )
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
            if start < datetime.datetime.now(tz=start.tzinfo):
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
            recurrence_rule = clean_recurrence(recurrence)[0]
            recurrence_dict = clean_recurrence(recurrence)[1]
            data |= {"recurrence_rule": recurrence_rule, "recurrence": recurrence_dict}

        data |= {
            "summary": cleaned_data.get("summary"),
            "description": cleaned_data.get("description"),
            "color": str(cleaned_data.get("color")),
        }
        return data
