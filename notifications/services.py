from .models import Notification


# ======================================================
# SERVICIO CENTRAL DE NOTIFICACIONES
# ======================================================

def create_notification(
    user,
    notification_type,
    title,
    message,
    appointment_id=None
):
    """
    Crea una notificación para un usuario.

    Este servicio centraliza la creación de
    notificaciones del sistema.
    """

    if not user:
        return None

    notification = Notification.objects.create(

        user=user,

        notification_type=notification_type,

        title=title,

        message=message,

        appointment_id=appointment_id

    )

    return notification


# ======================================================
# NUEVA CITA
# ======================================================

def notify_new_appointment(appointment):

    patient = appointment.patient

    appointment_type = (
        appointment.get_appointment_type_display()
    )

    create_notification(

        user=patient,

        notification_type="new_appointment",

        title="Nueva cita",

        message=(
            "Tu cita médica fue registrada correctamente. "
            f"Tipo: {appointment_type}. "
            f"Fecha: {appointment.date}. "
            f"Hora: {appointment.time.strftime('%H:%M')}."
        ),

        appointment_id=appointment.id

    )


# ======================================================
# CITA CONFIRMADA
# ======================================================

def notify_appointment_confirmed(appointment):

    patient = appointment.patient

    create_notification(

        user=patient,

        notification_type="appointment_confirmed",

        title="Cita confirmada",

        message=(
            "Tu cita médica fue confirmada correctamente. "
            f"Fecha: {appointment.date}. "
            f"Hora: {appointment.time.strftime('%H:%M')}."
        ),

        appointment_id=appointment.id

    )


# ======================================================
# CITA CANCELADA
# ======================================================

def notify_appointment_cancelled(appointment):

    patient = appointment.patient

    create_notification(

        user=patient,

        notification_type="appointment_cancelled",

        title="Cita cancelada",

        message=(
            "Tu cita médica fue cancelada. "
            f"Fecha: {appointment.date}. "
            f"Hora: {appointment.time.strftime('%H:%M')}."
        ),

        appointment_id=appointment.id

    )


# ======================================================
# CITA REPROGRAMADA
# ======================================================

def notify_appointment_rescheduled(appointment):

    patient = appointment.patient

    create_notification(

        user=patient,

        notification_type="appointment_rescheduled",

        title="Cita reprogramada",

        message=(
            "Tu cita médica fue reprogramada. "
            f"Nueva fecha: {appointment.date}. "
            f"Nueva hora: {appointment.time.strftime('%H:%M')}."
        ),

        appointment_id=appointment.id

    )

