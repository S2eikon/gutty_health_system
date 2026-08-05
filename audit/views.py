from rest_framework.decorators import (
    api_view,
    permission_classes
)

from rest_framework.permissions import (
    IsAuthenticated,
    IsAdminUser
)

from rest_framework.response import Response
from rest_framework import status

from .models import AuditLog
from .serializers import AuditLogSerializer

from .services import create_audit


# =====================================================
# LISTAR REGISTROS DE AUDITORÍA
# GET /audit/api/
#
# SOLO ADMINISTRADORES
# =====================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdminUser])
def audit_logs_api(request):

    # =================================================
    # CONSULTAR REGISTROS
    # =================================================

    logs = AuditLog.objects.all().order_by(
        "-created_at"
    )

    # =================================================
    # FILTRO POR MÓDULO
    #
    # Ejemplo:
    # /audit/api/?module=documents
    # =================================================

    module = request.GET.get("module")

    if module:

        logs = logs.filter(
            module__iexact=module
        )

    # =================================================
    # FILTRO POR ACCIÓN
    #
    # Ejemplo:
    # /audit/api/?action=create
    # =================================================

    action = request.GET.get("action")

    if action:

        logs = logs.filter(
            action=action
        )

    # =================================================
    # FILTRO POR USUARIO
    #
    # Ejemplo:
    # /audit/api/?user=ruben
    # =================================================

    username = request.GET.get("user")

    if username:

        logs = logs.filter(
            user__username__icontains=username
        )

    # =================================================
    # SERIALIZAR
    # =================================================

    serializer = AuditLogSerializer(
        logs,
        many=True
    )

    # =================================================
    # RESPUESTA
    # =================================================

    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )


# =====================================================
# CREAR REGISTRO DE AUDITORÍA
# POST /audit/api/create/
#
# SOLO ADMINISTRADORES
# =====================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdminUser])
def create_audit_api(request):

    # =================================================
    # VALIDAR INFORMACIÓN
    # =================================================

    serializer = AuditLogSerializer(
        data=request.data
    )

    if serializer.is_valid():

        # =================================================
        # CREAR REGISTRO
        # =================================================

        audit_log = serializer.save(
            user=request.user
        )

        # =================================================
        # RESPUESTA
        # =================================================

        return Response(
            AuditLogSerializer(audit_log).data,
            status=status.HTTP_201_CREATED
        )

    # =================================================
    # ERROR DE VALIDACIÓN
    # =================================================

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )