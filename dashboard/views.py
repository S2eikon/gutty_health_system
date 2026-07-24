from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from appointments.models import Appointment


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def citas_por_estado(request):

    total = Appointment.objects.count()

    confirmed = Appointment.objects.filter(
        status="confirmed"
    ).count()

    pending = Appointment.objects.filter(
        status="pending"
    ).count()

    cancelled = Appointment.objects.filter(
        status="cancelled"
    ).count()

    data = {

        "total": total,

        "confirmed": confirmed,

        "pending": pending,

        "cancelled": cancelled,

        "confirmed_percent":
            round((confirmed / total) * 100, 1)
            if total else 0,

        "pending_percent":
            round((pending / total) * 100, 1)
            if total else 0,

        "cancelled_percent":
            round((cancelled / total) * 100, 1)
            if total else 0

    }

    return Response(data)