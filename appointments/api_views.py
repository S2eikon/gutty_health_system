from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import Appointment
from .serializers import AppointmentSerializer


# =========================================================
# 📥 LISTAR CITAS
# =========================================================
@api_view(['GET'])
@permission_classes([AllowAny])
def api_appointments(request):

    appointments = Appointment.objects.all().order_by('-created_at')

    serializer = AppointmentSerializer(
        appointments,
        many=True
    )

    return Response(serializer.data)


# =========================================================
# ➕ CREAR CITA
# =========================================================
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def api_create_appointment(request):

    data = request.data.copy()

    # ⚠️ TEMPORAL PARA PRUEBAS
    data['patient'] = 3
    data['doctor'] = 2

    serializer = AppointmentSerializer(data=data)

    if serializer.is_valid():

        try:
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        except Exception as e:

            return Response(
                {
                    'error': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# =========================================================
# ❌ ELIMINAR CITA
# =========================================================
@api_view(['DELETE'])
@permission_classes([AllowAny])
def api_delete_appointment(request, appointment_id):

    try:

        appointment = Appointment.objects.get(id=appointment_id)

        appointment.delete()

        return Response(
            {
                'message': 'Cita eliminada correctamente'
            },
            status=status.HTTP_200_OK
        )

    except Appointment.DoesNotExist:

        return Response(
            {
                'error': 'La cita no existe'
            },
            status=status.HTTP_404_NOT_FOUND
        )


# =========================================================
# ✅ CONFIRMAR CITA
# =========================================================
@api_view(['PATCH'])
@permission_classes([AllowAny])
def confirm_appointment(request, appointment_id):

    try:

        appointment = Appointment.objects.get(id=appointment_id)

        appointment.status = 'confirmed'
        appointment.save()

        return Response(
            {
                'message': 'Cita confirmada'
            },
            status=status.HTTP_200_OK
        )

    except Appointment.DoesNotExist:

        return Response(
            {
                'error': 'La cita no existe'
            },
            status=status.HTTP_404_NOT_FOUND
        )


# =========================================================
# ❌ CANCELAR CITA
# =========================================================
@api_view(['PATCH'])
@permission_classes([AllowAny])
def cancel_appointment(request, appointment_id):

    try:

        appointment = Appointment.objects.get(id=appointment_id)

        appointment.status = 'cancelled'
        appointment.save()

        return Response(
            {
                'message': 'Cita cancelada'
            },
            status=status.HTTP_200_OK
        )

    except Appointment.DoesNotExist:

        return Response(
            {
                'error': 'La cita no existe'
            },
            status=status.HTTP_404_NOT_FOUND
        )


# =========================================================
# 🔄 REPROGRAMAR CITA
# =========================================================
@api_view(['PATCH'])
@permission_classes([AllowAny])
def reschedule_appointment(request, appointment_id):

    try:

        appointment = Appointment.objects.get(id=appointment_id)

        appointment.status = 'rescheduled'
        appointment.save()

        return Response(
            {
                'message': 'Cita reprogramada'
            },
            status=status.HTTP_200_OK
        )

    except Appointment.DoesNotExist:

        return Response(
            {
                'error': 'La cita no existe'
            },
            status=status.HTTP_404_NOT_FOUND
        )