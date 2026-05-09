from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import Appointment
from .serializers import AppointmentSerializer


# =========================
# 📥 LISTAR CITAS
# =========================
@api_view(['GET'])
@permission_classes([AllowAny])
def api_appointments(request):
    appointments = Appointment.objects.all()
    serializer = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data)


# =========================
# ➕ CREAR CITA
# =========================
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def api_create_appointment(request):

    data = request.data.copy()

    # ⚠️ TEMPORAL (para pruebas)
    data['patient'] = 3
    data['doctor'] = 2

    serializer = AppointmentSerializer(data=data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)