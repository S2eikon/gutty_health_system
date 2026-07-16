from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from users.permissions import (
    IsAdmin,
    IsAdminOrDoctor,
    IsAdminOrPatient,
    IsAdminOrReceptionist,
)
from .models import Appointment
from .serializers import AppointmentSerializer


# ======================================================
# LISTAR CITAS
# ======================================================
@api_view(["GET"])
@permission_classes([IsAdminOrPatient])
def appointments_api(request):

    print("=" * 60)
    print("USER:", request.user)
    print("ROLE:", request.user.role)
    print("AUTH HEADER:", request.headers.get("Authorization"))
    print("=" * 60)

    appointments = Appointment.objects.all().order_by("-created_at")

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

        return Response(serializer.data, status=201)

    print(serializer.errors)

    return Response(serializer.errors, status=400)


# ======================================================
# ACTUALIZAR CITA
# ======================================================
@api_view(["PUT"])
@permission_classes([IsAdminOrPatient])
def update_appointment_api(request, appointment_id):

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

        serializer.save(patient=request.user)

        return Response(serializer.data)

    print(serializer.errors)

    return Response(serializer.errors, status=400)


# ======================================================
# CONFIRMAR CITA
# ======================================================
@api_view(["PATCH"])
@permission_classes([IsAdminOrDoctor])
def confirm_appointment_api(request, appointment_id):

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id
    )

    appointment.status = "confirmed"
    appointment.save()

    return Response({
        "message": "Cita confirmada"
    })


# ======================================================
# CANCELAR CITA
# ======================================================
@api_view(["PATCH"])
@permission_classes([IsAdminOrDoctor])
def cancel_appointment_api(request, appointment_id):

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id
    )

    appointment.status = "cancelled"
    appointment.save()

    return Response({
        "message": "Cita cancelada"
    })


# ======================================================
# REPROGRAMAR CITA
# ======================================================
@api_view(["PATCH"])
@permission_classes([IsAdminOrReceptionist])
def reschedule_appointment_api(request, appointment_id):

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id
    )

    appointment.status = "rescheduled"
    appointment.save()

    return Response({
        "message": "Cita reprogramada"
    })


# ======================================================
# ELIMINAR CITA
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
