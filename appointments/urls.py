# ======================================================
# APPOINTMENTS / URLS.PY
# GUTTY HEALTH SYSTEM
# ======================================================

from django.urls import path

from . import views


# ======================================================
# URLS - CITAS
# ======================================================

urlpatterns = [

    # ==================================================
    # LISTAR CITAS
    # GET /appointments/api/
    #
    # PAGINACIÓN:
    #
    # /appointments/api/?page=1
    # /appointments/api/?page=2
    # /appointments/api/?page=3
    #
    # Cada página devuelve máximo 20 citas.
    #
    # También se admite:
    #
    # /appointments/api/?page=2&page_size=20
    #
    # La paginación y el límite máximo de registros
    # están controlados en appointments/views.py.
    # ==================================================

    path(
        "api/",
        views.appointments_api,
        name="appointments_api",
    ),


    # ==================================================
    # CREAR CITA
    # POST /appointments/api/create/
    # ==================================================

    path(
        "api/create/",
        views.create_appointment_api,
        name="create_appointment",
    ),


    # ==================================================
    # ACTUALIZAR CITA
    # PUT /appointments/api/<id>/update/
    # ==================================================

    path(
        "api/<int:appointment_id>/update/",
        views.update_appointment_api,
        name="update_appointment",
    ),


    # ==================================================
    # CONFIRMAR CITA
    # PATCH /appointments/api/<id>/confirm/
    # ==================================================

    path(
        "api/<int:appointment_id>/confirm/",
        views.confirm_appointment_api,
        name="confirm_appointment",
    ),


    # ==================================================
    # CANCELAR CITA
    # PATCH /appointments/api/<id>/cancel/
    # ==================================================

    path(
        "api/<int:appointment_id>/cancel/",
        views.cancel_appointment_api,
        name="cancel_appointment",
    ),


    # ==================================================
    # REPROGRAMAR CITA
    # PATCH /appointments/api/<id>/reschedule/
    # ==================================================

    path(
        "api/<int:appointment_id>/reschedule/",
        views.reschedule_appointment_api,
        name="reschedule_appointment",
    ),


    # ==================================================
    # ELIMINAR CITA
    # DELETE /appointments/api/<id>/delete/
    # ==================================================

    path(
        "api/<int:appointment_id>/delete/",
        views.delete_appointment_api,
        name="delete_appointment",
    ),


    # ==================================================
    # ENVIAR RECORDATORIO INDIVIDUAL
    # POST /appointments/api/<id>/send-reminder/
    # ==================================================

    path(
        "api/<int:appointment_id>/send-reminder/",
        views.send_reminder_api,
        name="send_reminder",
    ),


    # ==================================================
    # ENVIAR TODOS LOS RECORDATORIOS PENDIENTES
    # POST /appointments/api/send-reminders/
    # ==================================================

    path(
        "api/send-reminders/",
        views.send_pending_reminders_api,
        name="send_pending_reminders",
    ),


    # ==================================================
    # DASHBOARD
    # GET /appointments/api/dashboard/
    #
    # Devuelve únicamente los totales estadísticos
    # de las citas.
    # ==================================================

    path(
        "api/dashboard/",
        views.dashboard_totals_api,
        name="dashboard_totals",
    ),


    # ==================================================
    # CALENDARIO
    # GET /appointments/api/calendar/
    #
    # Endpoint independiente del listado paginado.
    #
    # /appointments/api/
    #     -> listado paginado
    #
    # /appointments/api/calendar/
    #     -> eventos para FullCalendar
    #
    # La auditoría de la consulta del calendario se
    # encuentra implementada en views.py.
    # ==================================================

    path(
        "api/calendar/",
        views.calendar_appointments_api,
        name="calendar_appointments",
    ),

]