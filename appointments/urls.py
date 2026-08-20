# ======================================================

# APPOINTMENTS / URLS.PY

# GUTTY HEALTH SYSTEM

# ======================================================

from django.urls import path

from . import views

# ======================================================

# URLS DEL MÓDULO DE CITAS

# ======================================================

urlpatterns = [


# ==================================================
# LISTAR CITAS
# GET /appointments/api/
# ==================================================

path(
    "api/",
    views.appointments_api,
    name="appointments",
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
# RECORDATORIO INDIVIDUAL
# POST /appointments/api/<id>/reminder/
# ==================================================

path(
    "api/<int:appointment_id>/reminder/",
    views.send_reminder_api,
    name="send_reminder",
),

# ==================================================
# RECORDATORIO INDIVIDUAL - COMPATIBILIDAD FRONTEND
# POST /appointments/api/<id>/send-reminder/
# ==================================================

path(
    "api/<int:appointment_id>/send-reminder/",
    views.send_reminder_api,
    name="send_reminder_legacy",
),

# ==================================================
# RECORDATORIOS PENDIENTES
# POST /appointments/api/reminders/pending/
# ==================================================

path(
    "api/reminders/pending/",
    views.send_pending_reminders_api,
    name="send_pending_reminders",
),

# ==================================================
# DASHBOARD
# GET /appointments/api/dashboard/
# ==================================================

path(
    "api/dashboard/",
    views.dashboard_totals_api,
    name="dashboard_totals",
),

# ==================================================
# CALENDARIO
# GET /appointments/api/calendar/
# ==================================================

path(
    "api/calendar/",
    views.calendar_appointments_api,
    name="calendar_appointments",
),


]
