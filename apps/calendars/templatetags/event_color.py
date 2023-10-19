from django import template

from apps.calendars.forms import COLOR_CHOICES

register = template.Library()


@register.simple_tag
def event_color(color_id):
    if color_id:
        return f"background-color: {COLOR_CHOICES[int(color_id) - 1][1]}"
