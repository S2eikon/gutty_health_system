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
        appointments = Appointment.objects.filter(patient=request.user).order_by("-created_at")
    else:
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

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    print(serializer.errors)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

    # Validar estado antes de confirmar
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
# CANCELAR CITA
# ======================================================
@api_view(["PATCH"])
@permission_classes([IsAdminOrDoctor])
def cancel_appointment_api(request, appointment_id):

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id
    )

    # Validar estado antes de cancelar
    if appointment.status == "cancelled":
        return Response(
            {"error": "La cita ya fue cancelada"},
            status=status.HTTP_400_BAD_REQUEST
        )
    # Permitir cancelar citas confirmadas, por eso no hay restricción aquí

    appointment.status = "cancelled"
    appointment.save(update_fields=["status"])

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

    # Validar estado antes de reprogramar
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
