from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from users.permissions import (
    IsAdmin,
    IsAdminOrDoctor,
    IsAdminOrPatient,
    IsAdminOrReceptionist,
    IsAdminDoctorPatientReceptionist,
)

from .models import Appointment
from .serializers import AppointmentSerializer

# Nuevos imports para recordatorios
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings


# ======================================================
# LISTAR CITAS
# ======================================================
@api_view(["GET"])
@permission_classes([IsAdminDoctorPatientReceptionist])
def appointments_api(request):

    print("=" * 60)
    print("USER:", request.user)
    print("ROLE:", request.user.role)
    print("AUTH HEADER:", request.headers.get("Authorization"))
    print("=" * 60)

    if request.user.role == "patient":
        appointments = Appointment.objects.filter(
            patient=request.user
        ).order_by("date", "time")
    else:
        appointments = Appointment.objects.all().order_by("date", "time")

    serializer = AppointmentSerializer(
        appointments,
        many=True
    )

    return Response(serializer.data)


# ======================================================
# CREAR CITA
# ======================================================
@api_view(["POST"])
@permission_classes([IsAdminOrPatient])
def create_appointment_api(request):

    print("=" * 60)
    print("USER:", request.user)
    print("ROLE:", request.user.role)
    print("DATA:", request.data)
    print("=" * 60)

    serializer = AppointmentSerializer(data=request.data)

    if serializer.is_valid():

        serializer.save(patient=request.user)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    print(serializer.errors)

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# ======================================================
# ACTUALIZAR CITA
# ======================================================
@api_view(["PUT"])
@permission_classes([IsAdminOrPatient])
def update_appointment_api(request, appointment_id):

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
            serializer.save(patient=request.user)
        else:
            serializer.save()

        return Response(serializer.data)

    print(serializer.errors)

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# ======================================================
# CONFIRMAR
# ======================================================
@api_view(["PATCH"])
@permission_classes([IsAdminOrDoctor])
def confirm_appointment_api(request, appointment_id):

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id
    )

    if appointment.status == "confirmed":
        return Response(
            {"error": "La cita ya está confirmada"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if appointment.status == "cancelled":
        return Response(
            {"error": "No se puede confirmar una cita cancelada"},
            status=status.HTTP_400_BAD_REQUEST
        )

    appointment.status = "confirmed"
    appointment.save(update_fields=["status"])

    return Response({
        "message": "Cita confirmada"
    })


# ======================================================
# CANCELAR
# ======================================================
@api_view(["PATCH"])
@permission_classes([IsAdminOrDoctor])
def cancel_appointment_api(request, appointment_id):

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id
    )

    if appointment.status == "cancelled":
        return Response(
            {"error": "La cita ya fue cancelada"},
            status=status.HTTP_400_BAD_REQUEST
        )

    appointment.status = "cancelled"
    appointment.save(update_fields=["status"])

    return Response({
        "message": "Cita cancelada"
    })


# ======================================================
# REPROGRAMAR
# ======================================================
@api_view(["PATCH"])
@permission_classes([IsAdminOrReceptionist])
def reschedule_appointment_api(request, appointment_id):

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id
    )

    if appointment.status == "cancelled":
        return Response(
            {"error": "No se puede reprogramar una cita cancelada"},
            status=status.HTTP_400_BAD_REQUEST
        )

    appointment.status = "rescheduled"
    appointment.save(update_fields=["status"])

    return Response({
        "message": "Cita reprogramada"
    })


# ======================================================
# ELIMINAR
# ======================================================
@api_view(["DELETE"])
@permission_classes([IsAdmin])
def delete_appointment_api(request, appointment_id):

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id
    )

    appointment.delete()

    return Response({
        "message": "Cita eliminada"
    })


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
        "pending": appointments.filter(status="pending").count(),
        "confirmed": appointments.filter(status="confirmed").count(),
        "cancelled": appointments.filter(status="cancelled").count(),
        "rescheduled": appointments.filter(status="rescheduled").count(),
    }

    return Response(data)


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

            "title": f"{patient_name} - {appointment.get_appointment_type_display()}",

            "start": f"{appointment.date}T{appointment.time}",

            "color": STATUS_COLORS.get(
                appointment.status,
                "#6c757d"
            ),

            "extendedProps": {

                "patient": patient_name,

                "doctor": doctor_name,

                "status": appointment.status,

                "status_display": appointment.get_status_display(),

                "appointment_type": appointment.get_appointment_type_display(),

                "date": str(appointment.date),

                "time": str(appointment.time)[:5],

                "notes": getattr(appointment, "notes", ""),

                "phone": getattr(appointment.patient, "phone", ""),

                "email": appointment.patient.email,

            }

        })

    return Response(events)


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

    return Response(
        {
            "message": f"Se enviaron {enviados} recordatorios."
        },
        status=status.HTTP_200_OK
    )


# ======================================================
# ENVIAR RECORDATORIO POR CORREO
# ======================================================
@api_view(["POST"])
@permission_classes([IsAdminDoctorPatientReceptionist])
def send_reminder_api(request, appointment_id):

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id
    )

    if not appointment.patient.email:

        return Response(
            {
                "error": "El paciente no tiene un correo registrado."
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

    return Response(
        {
            "message": "Recordatorio enviado correctamente."
        },
        status=status.HTTP_200_OK
    )

