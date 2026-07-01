from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Appointment
from .serializers import AppointmentSerializer


@api_view(['GET'])
def appointments_api(request):

    appointments = Appointment.objects.all().order_by('-created_at')

    serializer = AppointmentSerializer(
        appointments,
        many=True
    )

    return Response(serializer.data)


@api_view(['PUT'])
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


@api_view(['DELETE'])
def delete_appointment_api(request, appointment_id):

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id
    )

    appointment.delete()

    return Response({
        "message": "Cita eliminada"
    })