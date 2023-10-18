# urls.py
from django.urls import path
from . import views

app_name = "calendars"

urlpatterns = [
    path('list/', views.list_event, name='list'),
    path('<event_id>/update/', views.update_event, name='update'),
    path('<event_id>/delete/', views.delete_event, name='delete'),
    path('<event_id/', views.get_event, name='details'),
    path('create/', views.create_event, name='create'),
    # path("recurrence/", views.recurrence, name="recurrence"),
]
