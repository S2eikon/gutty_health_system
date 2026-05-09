from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Appointment
from .serializers import AppointmentSerializer


# =========================
# 📥 LISTAR CITAS (para urls.py)
# =========================
@api_view(['GET'])
@permission_classes([AllowAny])
def appointments_api(request):
    appointments = Appointment.objects.all()
    serializer = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data)


# =========================
# ❌ DETALLE + ELIMINAR
# =========================
@api_view(['GET', 'DELETE'])
@permission_classes([AllowAny])
def appointment_detail_api(request, appointment_id):

    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == 'GET':
        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data)

    appointment.delete()
    return Response({"message": "Cita eliminada"}, status=200)