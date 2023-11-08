from django import template

from apps.calendars.forms import COLOR_VALUES

register = template.Library()


@register.simple_tag
def event_colors():
    return COLOR_VALUES
