from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from appointments.models import Appointment

from audit.services import create_audit


# =====================================================
# DASHBOARD - CITAS POR ESTADO
# =====================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def citas_por_estado(request):

    # =================================================
    # TOTAL DE CITAS
    # =================================================

    total = Appointment.objects.count()

    # =================================================
    # CITAS CONFIRMADAS
    # =================================================

    confirmed = Appointment.objects.filter(
        status="confirmed"
    ).count()

    # =================================================
    # CITAS PENDIENTES
    # =================================================

    pending = Appointment.objects.filter(
        status="pending"
    ).count()

    # =================================================
    # CITAS CANCELADAS
    # =================================================

    cancelled = Appointment.objects.filter(
        status="cancelled"
    ).count()

    # =================================================
    # CALCULAR PORCENTAJES
    # =================================================

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

    # =================================================
    # AUDITORÍA - CONSULTAR DASHBOARD
    # =================================================

    create_audit(

        user=request.user,

        action="read",

        module="dashboard",

        object_id=None,

        description=(
            f"El usuario {request.user.username} "
            f"consultó las estadísticas de citas "
            f"del dashboard."
        ),

        request=request

    )

    # =================================================
    # RESPUESTA
    # =================================================

    return Response(
        data
    )

