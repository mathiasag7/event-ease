from django import template

from apps.calendars.forms import COLOR_CHOICES, COLOR_VALUES

register = template.Library()


@register.simple_tag
def event_color(color_id):
    if color_id:
        color_id = int(color_id)
        color_name = COLOR_CHOICES[color_id - 1][1]

        return f"background-color: {COLOR_VALUES[color_name]}"
