from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Appointment
from .serializers import AppointmentSerializer


# =========================
# 📥 LISTAR CITAS
# =========================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def appointments_api(request):

    print("USER AUTH:", request.user)
    print("AUTH HEADER:", request.headers.get('Authorization'))

    appointments = Appointment.objects.all().order_by('-created_at')

    serializer = AppointmentSerializer(
        appointments,
        many=True
    )

    return Response(serializer.data)


# =========================
# ✏️ ACTUALIZAR CITA
# =========================
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
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
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=400)


# =========================
# ❌ ELIMINAR CITA
# =========================
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_appointment_api(request, appointment_id):

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id
    )

    appointment.delete()

    return Response({
        "message": "Cita eliminada"
    })
