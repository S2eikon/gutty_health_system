from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from .models import AuditLog
from .serializers import AuditLogSerializer



# =====================================================
# LISTAR REGISTROS DE AUDITORÍA
# GET /audit/api/
# =====================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def audit_logs_api(request):

    logs = AuditLog.objects.all()


    # ================================================
    # FILTRO POR MÓDULO
    # Ejemplo:
    # /audit/api/?module=Documents
    # ================================================

    module = request.GET.get("module")

    if module:

        logs = logs.filter(
            module__iexact=module
        )


    # ================================================
    # FILTRO POR ACCIÓN
    # Ejemplo:
    # /audit/api/?action=create
    # ================================================

    action = request.GET.get("action")

    if action:

        logs = logs.filter(
            action=action
        )


    # ================================================
    # FILTRO POR USUARIO
    # Ejemplo:
    # /audit/api/?user=admin
    # ================================================

    username = request.GET.get("user")

    if username:

        logs = logs.filter(
            user__username__icontains=username
        )


    serializer = AuditLogSerializer(
        logs,
        many=True
    )


    return Response(

        serializer.data,

        status=status.HTTP_200_OK

    )



# =====================================================
# CREAR REGISTRO DE AUDITORÍA
# POST /audit/api/create/
# =====================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_audit_api(request):

    serializer = AuditLogSerializer(

        data=request.data

    )


    if serializer.is_valid():

        serializer.save(

            user=request.user

        )


        return Response(

            serializer.data,

            status=status.HTTP_201_CREATED

        )


    return Response(

        serializer.errors,

        status=status.HTTP_400_BAD_REQUEST

    )