from django.urls import path
from . import views

urlpatterns = [

    path(
        "api/",
        views.appointments_api,
        name="appointments_api"
    ),

    path(
        "api/create/",
        views.create_appointment_api,
        name="create_appointment"
    ),

    path(
        "api/<int:appointment_id>/update/",
        views.update_appointment_api,
        name="update_appointment"
    ),

    path(
        "api/<int:appointment_id>/confirm/",
        views.confirm_appointment_api,
        name="confirm_appointment"
    ),

    path(
        "api/<int:appointment_id>/cancel/",
        views.cancel_appointment_api,
        name="cancel_appointment"
    ),

    path(
        "api/<int:appointment_id>/reschedule/",
        views.reschedule_appointment_api,
        name="reschedule_appointment"
    ),

    path(
        "api/<int:appointment_id>/delete/",
        views.delete_appointment_api,
        name="delete_appointment"
    ),

    # Nueva ruta para dashboard con totales por estado
    path(
        "api/dashboard/",
        views.dashboard_totals_api,
        name="dashboard_totals"
    ),

    # Nueva ruta para el calendario de citas
    path(
        "api/calendar/",
        views.calendar_appointments_api,
        name="calendar_appointments"
    ),
]
