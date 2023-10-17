import datetime
from django import forms


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


class CalendarCreateEditForm(forms.Form):

    summary = forms.CharField(
        label="Summary",
    )
    description = forms.CharField(label="Description", required=False)

    start = forms.DateTimeField(
        label="Start",
        widget=forms.DateTimeInput(
            attrs={
                "type": "datetime-local",
            }
        ),
    )
    end = forms.DateTimeField(
        label="End",
        required=False,
        widget=forms.DateTimeInput(
            attrs={
                "type": "datetime-local",
            }
        ),
    )
    color = forms.ChoiceField(
        choices=COLOR_CHOICES,
        label="Color",
        required=False,
    )
    recurrence  = forms.CharField(
        label="Recurrence",
        required=False,
        
    )

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start")
        end = cleaned_data.get("end")
        if not start:
            raise forms.ValidationError("Start is required.")
        if start < datetime.datetime.now(tz=start.tzinfo):
            raise forms.ValidationError("Start must be in the future.")
        if end and start > end:
            raise forms.ValidationError("Start must be before end.")

        timezone = start.tzinfo
        return {
            "summary": cleaned_data.get("summary"),
            "description": cleaned_data.get("description"),
            "start": start,
            "end": end.astimezone(timezone) if end else None,
            "color": str(cleaned_data.get("color")),
            "timezone": str(timezone),
        }


    # location = forms.CharField(
    #     label="Location",
    #     required=False
    # )
    # recurrence = forms.CharField(
    #     label="Recurrence",
    #     required=False
    # )
    # visibility = forms.ChoiceField(
    #     label="Visibility",
    #     choices=[
    #         (Visibility.DEFAULT, "Default"),
    #         (Visibility.PUBLIC, "Public"),
    #         (Visibility.PRIVATE, "Private"),
    #     ],
    #     required=False
    # )
    # attendees = forms.CharField(
    #     label="Attendees",
    # )
    # email = forms.EmailField(
    #     label="Email"
    # )
    # display_name = forms.CharField(label="Display Name", required=False)
    # comment = forms.CharField(label="Comment", required=False)
    # optional = forms.BooleanField(
    #     label="Optional",
    #     required=False
    # )
    # is_resource = forms.BooleanField(label="Is Resource", required=False)
    # additional_guests = forms.IntegerField(label="Additional Guests", required=False)
