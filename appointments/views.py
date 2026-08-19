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

from .models import Appointment
from .serializers import AppointmentSerializer

from audit.services import create_audit


# ======================================================
# LISTAR CITAS
# ======================================================

@api_view(["GET"])
@permission_classes([IsAdminDoctorPatientReceptionist])
def appointments_api(request):

    print(
        "[AUDITORÍA][APPOINTMENTS] "
        "Consulta de listado de citas."
    )

    print(
        "[AUDITORÍA][APPOINTMENTS] "
        f"Usuario: {request.user.username}"
    )

    print(
        "[AUDITORÍA][APPOINTMENTS] "
        f"Rol: {request.user.role}"
    )

    if request.user.role == "patient":

        appointments = Appointment.objects.filter(
            patient=request.user
        ).order_by(
            "date",
            "time"
        )

    else:

        appointments = Appointment.objects.all().order_by(
            "date",
            "time"
        )

    # ==================================================
    # PAGINACIÓN
    # ==================================================

    paginator = PageNumberPagination()

    paginator.page_size = 20

    paginator.page_size_query_param = "page_size"

    paginator.max_page_size = 100

    paginated_appointments = paginator.paginate_queryset(
        appointments,
        request
    )

    serializer = AppointmentSerializer(
        paginated_appointments,
        many=True,
        context={
            "request": request
        }
    )

    # ==================================================
    # AUDITORÍA
    # ==================================================

    create_audit(
        user=request.user,
        action="read",
        module="appointments",
        object_id=None,
        description=(
            f"El usuario {request.user.username} "
            f"consultó la lista de citas."
        ),
        request=request
    )

    print(
        "[AUDITORÍA][APPOINTMENTS] "
        "Listado consultado correctamente."
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

    print(
        "[AUDITORÍA][APPOINTMENTS] "
        "Solicitud para crear cita."
    )

    print(
        "[AUDITORÍA][APPOINTMENTS] "
        f"Usuario: {request.user.username}"
    )

    print(
        "[AUDITORÍA][APPOINTMENTS] "
        f"Rol: {request.user.role}"
    )

    print(
        "[AUDITORÍA][APPOINTMENTS] "
        f"Datos recibidos: {request.data}"
    )

    serializer = AppointmentSerializer(
        data=request.data,
        context={
            "request": request
        }
    )

    if serializer.is_valid():

        appointment = serializer.save()

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
                f"creó la cita con ID {appointment.id}."
            ),
            request=request
        )

        print(
            "[AUDITORÍA][APPOINTMENTS] "
            "Cita creada correctamente."
        )

        return Response(
            AppointmentSerializer(
                appointment,
                context={
                    "request": request
                }
            ).data,
            status=status.HTTP_201_CREATED
        )

    print(
        "[AUDITORÍA][APPOINTMENTS] "
        f"Error de validación al crear cita: "
        f"{serializer.errors}"
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

    print(
        "[AUDITORÍA][APPOINTMENTS] "
        "Solicitud para actualizar cita."
    )

    print(
        "[AUDITORÍA][APPOINTMENTS] "
        f"Usuario: {request.user.username}"
    )

    print(
        "[AUDITORÍA][APPOINTMENTS] "
        f"Rol: {request.user.role}"
    )

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
        partial=True,
        context={
            "request": request
        }
    )

    if serializer.is_valid():

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

        print(
            "[AUDITORÍA][APPOINTMENTS] "
            "Cita actualizada correctamente."
        )

        return Response(
            AppointmentSerializer(
                appointment,
                context={
                    "request": request
                }
            ).data,
            status=status.HTTP_200_OK
        )

    print(
        "[AUDITORÍA][APPOINTMENTS] "
        f"Error de validación al actualizar: "
        f"{serializer.errors}"
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
                "error":
                "La cita ya está confirmada."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if appointment.status == "cancelled":

        return Response(
            {
                "error":
                "No se puede confirmar una cita cancelada."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    appointment.status = "confirmed"

    appointment.save(
        update_fields=["status"]
    )

    # ==================================================
    # AUDITORÍA
    # ==================================================

    create_audit(
        user=request.user,
        action="confirm",
        module="appointments",
        object_id=appointment.id,
        description=(
            f"El usuario {request.user.username} "
            f"confirmó la cita con ID {appointment.id}."
        ),
        request=request
    )

    return Response(
        {
            "message":
            "Cita confirmada correctamente."
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
                "error":
                "La cita ya fue cancelada."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    appointment.status = "cancelled"

    appointment.save(
        update_fields=["status"]
    )

    # ==================================================
    # AUDITORÍA
    # ==================================================

    create_audit(
        user=request.user,
        action="cancel",
        module="appointments",
        object_id=appointment.id,
        description=(
            f"El usuario {request.user.username} "
            f"canceló la cita con ID {appointment.id}."
        ),
        request=request
    )

    return Response(
        {
            "message":
            "Cita cancelada correctamente."
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
                "error":
                "No se puede reprogramar una cita cancelada."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = AppointmentSerializer(
        appointment,
        data=request.data,
        partial=True,
        context={
            "request": request
        }
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
    # AUDITORÍA
    # ==================================================

    create_audit(
        user=request.user,
        action="reschedule",
        module="appointments",
        object_id=appointment.id,
        description=(
            f"El usuario {request.user.username} "
            f"reprogramó la cita con ID {appointment.id}."
        ),
        request=request
    )

    return Response(
        {
            "message":
            "Cita reprogramada correctamente.",

            "appointment":
            AppointmentSerializer(
                appointment,
                context={
                    "request": request
                }
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
    # AUDITORÍA
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
            "message":
            "Cita eliminada correctamente."
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

        "total":
        appointments.count(),

        "pending":
        appointments.filter(
            status="pending"
        ).count(),

        "confirmed":
        appointments.filter(
            status="confirmed"
        ).count(),

        "cancelled":
        appointments.filter(
            status="cancelled"
        ).count(),

        "rescheduled":
        appointments.filter(
            status="rescheduled"
        ).count(),
    }

    # ==================================================
    # AUDITORÍA
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

        "pending":
        "#ffc107",

        "confirmed":
        "#198754",

        "cancelled":
        "#dc3545",

        "rescheduled":
        "#0dcaf0",
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

            "id":
            appointment.id,

            "title":
            f"{patient_name} - "
            f"{appointment.get_appointment_type_display()}",

            "start":
            f"{appointment.date}T{appointment.time}",

            "color":
            STATUS_COLORS.get(
                appointment.status,
                "#6c757d"
            ),

            "extendedProps": {

                "patient":
                patient_name,

                "doctor":
                doctor_name,

                "status":
                appointment.status,

                "status_display":
                appointment.get_status_display(),

                "appointment_type":
                appointment.get_appointment_type_display(),

                "date":
                str(appointment.date),

                "time":
                str(appointment.time)[:5],

                "notes":
                getattr(
                    appointment,
                    "notes",
                    ""
                ),

                "phone":
                getattr(
                    appointment.patient,
                    "phone",
                    ""
                ),

                "email":
                appointment.patient.email,
            }
        })

    # ==================================================
    # AUDITORÍA
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
Hola {appointment.patient.get_full_name() or appointment.patient.username},

Este es un recordatorio de su cita médica.

Fecha: {appointment.date}
Hora: {appointment.time.strftime('%H:%M')}
Doctor: {doctor_name}
Tipo de cita: {appointment.get_appointment_type_display()}

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
    # AUDITORÍA
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
            "message":
            f"Se enviaron {enviados} recordatorios."
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
                "error":
                "El paciente no tiene un correo registrado."
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
Hola {appointment.patient.get_full_name() or appointment.patient.username},

Este es un recordatorio de su cita médica.

Fecha: {appointment.date}
Hora: {appointment.time.strftime('%H:%M')}
Doctor: {doctor_name}
Tipo de cita: {appointment.get_appointment_type_display()}

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
    # AUDITORÍA
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
            "message":
            "Recordatorio enviado correctamente."
        },
        status=status.HTTP_200_OK
    )