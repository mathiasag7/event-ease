# urls.py
from django.urls import path

from . import views

app_name = "calendars"

urlpatterns = [
    path("", views.list_event, name="list"),
    path("<event_id>/update/", views.update_event, name="update"),
    path("<event_id>/delete/", views.delete_event, name="delete"),
    path("<event_id/", views.get_event, name="details"),
    path("create/", views.create_event, name="create"),
    path("switch-user/", views.switch_user, name="switch_user"),
    # path("recurrence/", views.recurrence, name="recurrence"),
]
