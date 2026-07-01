from django.urls import path
from . import views

urlpatterns = [

    path(
        'api/',
        views.appointments_api,
        name='api_appointments'
    ),

    path(
        'api/<int:appointment_id>/update/',
        views.update_appointment_api,
        name='update_appointment'
    ),

    path(
        'api/<int:appointment_id>/delete/',
        views.delete_appointment_api,
        name='delete_appointment'
    ),
]