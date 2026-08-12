from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from users.permissions import (
    IsAdmin,
    IsAdminOrDoctor,
    IsAdminOrPatient,
    IsAdminOrReceptionist,
    IsAdminDoctorPatientReceptionist,
)

from users.models import User

from .models import Appointment
from .serializers import AppointmentSerializer

from audit.services import create_audit

from notifications.models import Notification


# ======================================================
# LISTAR CITAS
# ======================================================

@api_view(["GET"])
@permission_classes([IsAdminDoctorPatientReceptionist])
def appointments_api(request):

    if request.user.role == "patient":

        appointments = Appointment.objects.filter(
            patient=request.user
        ).order_by(
            "-date",
            "-time",
            "-id"
        )

    else:

        appointments = Appointment.objects.all().order_by(
            "-date",
            "-time",
            "-id"
        )

    # ==================================================
    # PAGINACIÓN
    # ==================================================

    paginator = PageNumberPagination()

    paginator.page_size = 20

    paginator.page_size_query_param = "page_size"

    paginator.max_page_size = 20

    paginated_appointments = paginator.paginate_queryset(
        appointments,
        request
    )

    serializer = AppointmentSerializer(
        paginated_appointments,
        many=True
    )

    # ==================================================
    # AUDITORÍA - CONSULTAR CITAS
    # ==================================================

    create_audit(
        user=request.user,
        action="read",
        module="appointments",
        object_id=None,
        description=(
            f"El usuario {request.user.username} "
            f"consultó la lista de citas. "
            f"Página: {request.query_params.get('page', '1')}. "
            f"Registros por página: 20."
        ),
        request=request
    )

    return paginator.get_paginated_response(
        serializer.data
    )


# ======================================================
# CREAR CITA
# ======================================================

@api_view(["POST"])
@permission_classes([IsAdminOrPatient])
def create_appointment_api(request):

    serializer = AppointmentSerializer(
        data=request.data
    )

    if serializer.is_valid():

        appointment = serializer.save(
            patient=request.user
        )

        patient_name = (
            appointment.patient.get_full_name()
            or appointment.patient.username
        )

        appointment_type = (
            appointment.get_appointment_type_display()
        )

        appointment_date = appointment.date

        appointment_time = (
            appointment.time.strftime("%H:%M")
        )

        # ==================================================
        # NOTIFICACIÓN - NUEVA CITA
        # ==================================================

        if appointment.doctor:

            Notification.objects.create(

                user=appointment.doctor,

                notification_type="new_appointment",

                title="Nueva cita",

                message=(
                    f"Se ha creado una nueva cita para "
                    f"{patient_name}. "
                    f"Fecha: {appointment_date}. "
                    f"Hora: {appointment_time}. "
                    f"Tipo: {appointment_type}."
                ),

                appointment_id=appointment.id
            )

        else:

            staff_users = User.objects.filter(
                role__in=[
                    "admin",
                    "receptionist"
                ]
            )

            for user in staff_users:

                Notification.objects.create(

                    user=user,

                    notification_type="new_appointment",

                    title="Nueva cita",

                    message=(
                        f"Se ha creado una nueva cita para "
                        f"{patient_name}. "
                        f"Fecha: {appointment_date}. "
                        f"Hora: {appointment_time}. "
                        f"Tipo: {appointment_type}. "
                        f"La cita aún no tiene médico asignado."
                    ),

                    appointment_id=appointment.id
                )

        # ==================================================
        # AUDITORÍA - CREAR CITA
        # ==================================================

        create_audit(
            user=request.user,
            action="create",
            module="appointments",
            object_id=appointment.id,
            description=(
                f"El usuario {request.user.username} "
                f"creó la cita con ID {appointment.id}. "
                f"Se generó la notificación de nueva cita."
            ),
            request=request
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# ======================================================
# ACTUALIZAR CITA
# ======================================================

@api_view(["PUT"])
@permission_classes([IsAdminOrPatient])
def update_appointment_api(
    request,
    appointment_id
):

    if request.user.role == "patient":

        appointment = get_object_or_404(
            Appointment,
            id=appointment_id,
            patient=request.user
        )

    else:

        appointment = get_object_or_404(
            Appointment,
            id=appointment_id
        )

    serializer = AppointmentSerializer(
        appointment,
        data=request.data,
        partial=True
    )

    if serializer.is_valid():

        if request.user.role == "patient":

            appointment = serializer.save(
                patient=request.user
            )

        else:

            appointment = serializer.save()

        # ==================================================
        # AUDITORÍA - ACTUALIZAR CITA
        # ==================================================

        create_audit(
            user=request.user,
            action="update",
            module="appointments",
            object_id=appointment.id,
            description=(
                f"El usuario {request.user.username} "
                f"actualizó la cita con ID {appointment.id}."
            ),
            request=request
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# ======================================================
# CONFIRMAR CITA
# ======================================================

@api_view(["PATCH"])
@permission_classes([IsAdminOrDoctor])
def confirm_appointment_api(
    request,
    appointment_id
):

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id
    )

    if appointment.status == "confirmed":

        return Response(
            {
                "error": "La cita ya está confirmada."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if appointment.status == "cancelled":

        return Response(
            {
                "error": (
                    "No se puede confirmar "
                    "una cita cancelada."
                )
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    appointment.status = "confirmed"

    appointment.save(
        update_fields=["status"]
    )

    # ==================================================
    # NOTIFICACIÓN - CITA CONFIRMADA
    # ==================================================

    patient_name = (
        appointment.patient.get_full_name()
        or appointment.patient.username
    )

    Notification.objects.create(

        user=appointment.patient,

        notification_type="appointment_confirmed",

        title="Cita confirmada",

        message=(
            f"Hola {patient_name}, "
            f"su cita médica ha sido confirmada. "
            f"Fecha: {appointment.date}. "
            f"Hora: {appointment.time.strftime('%H:%M')}. "
            f"Tipo: "
            f"{appointment.get_appointment_type_display()}."
        ),

        appointment_id=appointment.id
    )

    # ==================================================
    # AUDITORÍA - CONFIRMAR CITA
    # ==================================================

    create_audit(
        user=request.user,
        action="confirm",
        module="appointments",
        object_id=appointment.id,
        description=(
            f"El usuario {request.user.username} "
            f"confirmó la cita con ID {appointment.id}. "
            f"Se generó la notificación de cita "
            f"confirmada para el paciente."
        ),
        request=request
    )

    return Response(
        {
            "message": "Cita confirmada correctamente."
        },
        status=status.HTTP_200_OK
    )


# ======================================================
# CANCELAR CITA
# ======================================================

@api_view(["PATCH"])
@permission_classes([IsAdminOrDoctor])
def cancel_appointment_api(
    request,
    appointment_id
):

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id
    )

    if appointment.status == "cancelled":

        return Response(
            {
                "error": "La cita ya fue cancelada."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    appointment.status = "cancelled"

    appointment.save(
        update_fields=["status"]
    )

    # ==================================================
    # NOTIFICACIÓN - CITA CANCELADA
    # ==================================================

    patient_name = (
        appointment.patient.get_full_name()
        or appointment.patient.username
    )

    Notification.objects.create(

        user=appointment.patient,

        notification_type="appointment_cancelled",

        title="Cita cancelada",

        message=(
            f"Hola {patient_name}, "
            f"su cita médica ha sido cancelada. "
            f"Fecha: {appointment.date}. "
            f"Hora: {appointment.time.strftime('%H:%M')}. "
            f"Tipo: "
            f"{appointment.get_appointment_type_display()}."
        ),

        appointment_id=appointment.id
    )

    # ==================================================
    # AUDITORÍA - CANCELAR CITA
    # ==================================================

    create_audit(
        user=request.user,
        action="cancel",
        module="appointments",
        object_id=appointment.id,
        description=(
            f"El usuario {request.user.username} "
            f"canceló la cita con ID {appointment.id}. "
            f"Se generó la notificación de cita "
            f"cancelada para el paciente."
        ),
        request=request
    )

    return Response(
        {
            "message": "Cita cancelada correctamente."
        },
        status=status.HTTP_200_OK
    )


# ======================================================
# REPROGRAMAR CITA
# ======================================================

@api_view(["PATCH"])
@permission_classes([IsAdminOrReceptionist])
def reschedule_appointment_api(
    request,
    appointment_id
):

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id
    )

    if appointment.status == "cancelled":

        return Response(
            {
                "error": (
                    "No se puede reprogramar "
                    "una cita cancelada."
                )
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = AppointmentSerializer(
        appointment,
        data=request.data,
        partial=True
    )

    if not serializer.is_valid():

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    appointment = serializer.save()

    appointment.status = "rescheduled"

    appointment.save(
        update_fields=["status"]
    )

    # ==================================================
    # NOTIFICACIÓN - CITA REPROGRAMADA
    # ==================================================

    patient_name = (
        appointment.patient.get_full_name()
        or appointment.patient.username
    )

    Notification.objects.create(

        user=appointment.patient,

        notification_type="appointment_rescheduled",

        title="Cita reprogramada",

        message=(
            f"Hola {patient_name}, "
            f"su cita médica ha sido reprogramada. "
            f"Nueva fecha: {appointment.date}. "
            f"Nueva hora: "
            f"{appointment.time.strftime('%H:%M')}. "
            f"Tipo: "
            f"{appointment.get_appointment_type_display()}."
        ),

        appointment_id=appointment.id
    )

    # ==================================================
    # AUDITORÍA - REPROGRAMAR CITA
    # ==================================================

    create_audit(
        user=request.user,
        action="reschedule",
        module="appointments",
        object_id=appointment.id,
        description=(
            f"El usuario {request.user.username} "
            f"reprogramó la cita con ID {appointment.id}. "
            f"Se generó la notificación de cita "
            f"reprogramada para el paciente."
        ),
        request=request
    )

    return Response(
        {
            "message": "Cita reprogramada correctamente.",
            "appointment": AppointmentSerializer(
                appointment
            ).data
        },
        status=status.HTTP_200_OK
    )


# ======================================================
# ELIMINAR CITA
# ======================================================

@api_view(["DELETE"])
@permission_classes([IsAdmin])
def delete_appointment_api(
    request,
    appointment_id
):

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id
    )

    appointment_id_deleted = appointment.id

    # ==================================================
    # AUDITORÍA - ELIMINAR CITA
    # ==================================================

    create_audit(
        user=request.user,
        action="delete",
        module="appointments",
        object_id=appointment_id_deleted,
        description=(
            f"El usuario {request.user.username} "
            f"eliminó la cita con ID "
            f"{appointment_id_deleted}."
        ),
        request=request
    )

    appointment.delete()

    return Response(
        {
            "message": "Cita eliminada correctamente."
        },
        status=status.HTTP_200_OK
    )


# ======================================================
# DASHBOARD
# ======================================================

@api_view(["GET"])
@permission_classes([IsAdminDoctorPatientReceptionist])
def dashboard_totals_api(request):

    if request.user.role == "patient":

        appointments = Appointment.objects.filter(
            patient=request.user
        )

    else:

        appointments = Appointment.objects.all()

    data = {

        "total": appointments.count(),

        "pending": appointments.filter(
            status="pending"
        ).count(),

        "confirmed": appointments.filter(
            status="confirmed"
        ).count(),

        "cancelled": appointments.filter(
            status="cancelled"
        ).count(),

        "rescheduled": appointments.filter(
            status="rescheduled"
        ).count(),

    }

    # ==================================================
    # AUDITORÍA - DASHBOARD
    # ==================================================

    create_audit(
        user=request.user,
        action="read",
        module="appointments",
        object_id=None,
        description=(
            f"El usuario {request.user.username} "
            f"consultó el resumen del dashboard "
            f"de citas."
        ),
        request=request
    )

    return Response(
        data,
        status=status.HTTP_200_OK
    )


# ======================================================
# CALENDARIO
# ======================================================

@api_view(["GET"])
@permission_classes([IsAdminDoctorPatientReceptionist])
def calendar_appointments_api(request):

    if request.user.role == "patient":

        appointments = Appointment.objects.filter(
            patient=request.user
        ).select_related(
            "patient",
            "doctor"
        ).order_by(
            "date",
            "time"
        )

    else:

        appointments = Appointment.objects.select_related(
            "patient",
            "doctor"
        ).order_by(
            "date",
            "time"
        )

    STATUS_COLORS = {

        "pending": "#ffc107",

        "confirmed": "#198754",

        "cancelled": "#dc3545",

        "rescheduled": "#0dcaf0",

    }

    events = []

    for appointment in appointments:

        patient_name = (
            appointment.patient.get_full_name()
            or appointment.patient.username
        )

        doctor_name = "Sin asignar"

        if appointment.doctor:

            doctor_name = (
                appointment.doctor.get_full_name()
                or appointment.doctor.username
            )

        events.append({

            "id": appointment.id,

            "title": (
                f"{patient_name} - "
                f"{appointment.get_appointment_type_display()}"
            ),

            "start": (
                f"{appointment.date}T"
                f"{appointment.time}"
            ),

            "color": STATUS_COLORS.get(
                appointment.status,
                "#6c757d"
            ),

            "extendedProps": {

                "patient": patient_name,

                "doctor": doctor_name,

                "status": appointment.status,

                "status_display": (
                    appointment.get_status_display()
                ),

                "appointment_type": (
                    appointment.get_appointment_type_display()
                ),

                "date": str(appointment.date),

                "time": str(appointment.time)[:5],

                "notes": getattr(
                    appointment,
                    "notes",
                    ""
                ),

                "phone": getattr(
                    appointment.patient,
                    "phone",
                    ""
                ),

                "email": appointment.patient.email,

            }

        })

    # ==================================================
    # AUDITORÍA - CALENDARIO
    # ==================================================

    create_audit(
        user=request.user,
        action="read",
        module="appointments",
        object_id=None,
        description=(
            f"El usuario {request.user.username} "
            f"consultó el calendario de citas."
        ),
        request=request
    )

    return Response(
        events,
        status=status.HTTP_200_OK
    )


# ======================================================
# ENVIAR RECORDATORIOS A TODAS LAS CITAS PENDIENTES
# ======================================================

@api_view(["POST"])
@permission_classes([IsAdminDoctorPatientReceptionist])
def send_pending_reminders_api(request):

    appointments = Appointment.objects.filter(
        status="pending",
        reminder_sent=False
    )

    enviados = 0

    for appointment in appointments:

        if not appointment.patient.email:
            continue

        doctor_name = "Sin asignar"

        if appointment.doctor:

            doctor_name = (
                appointment.doctor.get_full_name()
                or appointment.doctor.username
            )

        send_mail(

            "Recordatorio de cita médica",

            f"""
Hola {
                appointment.patient.get_full_name()
                or appointment.patient.username
            },

Este es un recordatorio de su cita médica.

Fecha: {appointment.date}
Hora: {appointment.time.strftime('%H:%M')}
Doctor: {doctor_name}
Tipo de cita: {
                appointment.get_appointment_type_display()
            }

Instituto Médico Asdrúbal Gutty
""",

            settings.DEFAULT_FROM_EMAIL,

            [appointment.patient.email],

            fail_silently=False,

        )

        appointment.reminder_sent = True

        appointment.reminder_sent_at = timezone.now()

        appointment.save(
            update_fields=[
                "reminder_sent",
                "reminder_sent_at"
            ]
        )

        enviados += 1

    # ==================================================
    # AUDITORÍA - RECORDATORIOS MASIVOS
    # ==================================================

    if enviados > 0:

        create_audit(
            user=request.user,
            action="response",
            module="appointments",
            object_id=None,
            description=(
                f"El usuario {request.user.username} "
                f"envió {enviados} recordatorio(s) "
                f"de citas médicas."
            ),
            request=request
        )

    return Response(
        {
            "message": (
                f"Se enviaron {enviados} "
                f"recordatorios."
            )
        },
        status=status.HTTP_200_OK
    )


# ======================================================
# ENVIAR RECORDATORIO POR CORREO
# ======================================================

@api_view(["POST"])
@permission_classes([IsAdminDoctorPatientReceptionist])
def send_reminder_api(
    request,
    appointment_id
):

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id
    )

    if not appointment.patient.email:

        return Response(
            {
                "error": (
                    "El paciente no tiene "
                    "un correo registrado."
                )
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    subject = "Recordatorio de cita médica"

    doctor_name = "Sin asignar"

    if appointment.doctor:

        doctor_name = (
            appointment.doctor.get_full_name()
            or appointment.doctor.username
        )

    message = f"""
Hola {
        appointment.patient.get_full_name()
        or appointment.patient.username
    },

Este es un recordatorio de su cita médica.

Fecha: {appointment.date}
Hora: {appointment.time.strftime('%H:%M')}
Doctor: {doctor_name}
Tipo de cita: {
        appointment.get_appointment_type_display()
    }

Por favor llegue con 15 minutos de anticipación.

Instituto Médico Asdrúbal Gutty
"""

    send_mail(

        subject,

        message,

        settings.DEFAULT_FROM_EMAIL,

        [appointment.patient.email],

        fail_silently=False,

    )

    appointment.reminder_sent = True

    appointment.reminder_sent_at = timezone.now()

    appointment.save(
        update_fields=[
            "reminder_sent",
            "reminder_sent_at"
        ]
    )

    # ==================================================
    # AUDITORÍA - RECORDATORIO INDIVIDUAL
    # ==================================================

    create_audit(
        user=request.user,
        action="response",
        module="appointments",
        object_id=appointment.id,
        description=(
            f"El usuario {request.user.username} "
            f"envió un recordatorio para la cita "
            f"{appointment.id}."
        ),
        request=request
    )

    return Response(
        {
            "message": (
                "Recordatorio enviado correctamente."
            )
        },
        status=status.HTTP_200_OK
    )