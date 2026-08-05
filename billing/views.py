from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Bill
from .serializers import BillSerializer

from audit.services import create_audit


# =====================================================
# ROLES AUTORIZADOS PARA FACTURACIÓN
# =====================================================

BILLING_ALLOWED_ROLES = [
    "admin",
    "receptionist",
]


# =====================================================
# VALIDAR PERMISOS DE FACTURACIÓN
# =====================================================

def has_billing_permission(request):
    """
    Verifica si el usuario tiene permisos para
    consultar o modificar información de facturación.
    """

    return request.user.role in BILLING_ALLOWED_ROLES


# =====================================================
# REGISTRAR ACCESO DENEGADO
# =====================================================

def audit_billing_denied(request, action):
    """
    Registra cualquier intento de acceso no autorizado
    al módulo de facturación.
    """

    create_audit(
        user=request.user,
        action="denied",
        module="billing",
        object_id=None,
        description=(
            f"El usuario {request.user.username} "
            f"con rol {request.user.role} "
            f"intentó realizar la acción '{action}' "
            f"en el módulo de facturación sin permisos."
        ),
        request=request
    )


# =====================================================
# LISTAR FACTURAS
# =====================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def bill_list(request):

    # =================================================
    # VALIDAR ROL
    # =================================================

    if not has_billing_permission(request):

        audit_billing_denied(
            request,
            "consultar facturas"
        )

        return Response(
            {
                "detail": (
                    "No tienes permisos para "
                    "consultar las facturas."
                )
            },
            status=status.HTTP_403_FORBIDDEN
        )

    # =================================================
    # OBTENER FACTURAS
    # =================================================

    bills = Bill.objects.all().order_by(
        "-created_at"
    )

    serializer = BillSerializer(
        bills,
        many=True
    )

    # =================================================
    # AUDITORÍA - CONSULTAR FACTURAS
    # =================================================

    create_audit(
        user=request.user,
        action="read",
        module="billing",
        object_id=None,
        description=(
            f"El usuario {request.user.username} "
            f"consultó la lista de facturas."
        ),
        request=request
    )

    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )


# =====================================================
# CREAR FACTURA
# =====================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def bill_create(request):

    # =================================================
    # VALIDAR ROL
    # =================================================

    if not has_billing_permission(request):

        audit_billing_denied(
            request,
            "crear factura"
        )

        return Response(
            {
                "detail": (
                    "No tienes permisos para "
                    "crear facturas."
                )
            },
            status=status.HTTP_403_FORBIDDEN
        )

    # =================================================
    # VALIDAR INFORMACIÓN
    # =================================================

    serializer = BillSerializer(
        data=request.data
    )

    if serializer.is_valid():

        # =============================================
        # GUARDAR FACTURA
        # =============================================

        bill = serializer.save()

        # =============================================
        # AUDITORÍA - CREAR FACTURA
        # =============================================

        create_audit(
            user=request.user,
            action="create",
            module="billing",
            object_id=bill.id,
            description=(
                f"El usuario {request.user.username} "
                f"creó la factura con ID {bill.id}."
            ),
            request=request
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    # =================================================
    # ERROR DE VALIDACIÓN
    # =================================================

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# =====================================================
# ACTUALIZAR FACTURA
# =====================================================

@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def bill_update(request, pk):

    # =================================================
    # VALIDAR ROL
    # =================================================

    if not has_billing_permission(request):

        audit_billing_denied(
            request,
            "actualizar factura"
        )

        return Response(
            {
                "detail": (
                    "No tienes permisos para "
                    "actualizar facturas."
                )
            },
            status=status.HTTP_403_FORBIDDEN
        )

    # =================================================
    # BUSCAR FACTURA
    # =================================================

    bill = get_object_or_404(
        Bill,
        pk=pk
    )

    # =================================================
    # ACTUALIZAR FACTURA
    # =================================================

    serializer = BillSerializer(
        bill,
        data=request.data,
        partial=True
    )

    # =================================================
    # VALIDAR INFORMACIÓN
    # =================================================

    if serializer.is_valid():

        bill = serializer.save()

        # =============================================
        # AUDITORÍA - ACTUALIZAR FACTURA
        # =============================================

        create_audit(
            user=request.user,
            action="update",
            module="billing",
            object_id=bill.id,
            description=(
                f"El usuario {request.user.username} "
                f"actualizó la factura con ID {bill.id}."
            ),
            request=request
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    # =================================================
    # ERROR DE VALIDACIÓN
    # =================================================

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# =====================================================
# ELIMINAR FACTURA
# =====================================================

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def bill_delete(request, pk):

    # =================================================
    # VALIDAR ROL
    # =================================================

    if not has_billing_permission(request):

        audit_billing_denied(
            request,
            "eliminar factura"
        )

        return Response(
            {
                "detail": (
                    "No tienes permisos para "
                    "eliminar facturas."
                )
            },
            status=status.HTTP_403_FORBIDDEN
        )

    # =================================================
    # BUSCAR FACTURA
    # =================================================

    bill = get_object_or_404(
        Bill,
        pk=pk
    )

    # =================================================
    # GUARDAR ID ANTES DE ELIMINAR
    # =================================================

    bill_id = bill.id

    # =================================================
    # AUDITORÍA - ELIMINAR FACTURA
    # =================================================

    create_audit(
        user=request.user,
        action="delete",
        module="billing",
        object_id=bill_id,
        description=(
            f"El usuario {request.user.username} "
            f"eliminó la factura con ID {bill_id}."
        ),
        request=request
    )

    # =================================================
    # ELIMINAR FACTURA
    # =================================================

    bill.delete()

    # =================================================
    # RESPUESTA
    # =================================================

    return Response(
        {
            "message": (
                "Factura eliminada correctamente."
            )
        },
        status=status.HTTP_200_OK
    )

