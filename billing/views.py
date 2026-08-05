from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Bill
from .serializers import BillSerializer

from audit.services import create_audit


# =====================================================
# LISTAR FACTURAS
# =====================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def bill_list(request):

    bills = Bill.objects.all().order_by('-created_at')

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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bill_create(request):

    serializer = BillSerializer(
        data=request.data
    )

    # =================================================
    # VALIDAR INFORMACIÓN
    # =================================================

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

        # =============================================
        # RESPUESTA
        # =============================================

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

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def bill_update(request, pk):

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

        # =============================================
        # RESPUESTA
        # =============================================

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

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def bill_delete(request, pk):

    # =================================================
    # BUSCAR FACTURA
    # =================================================

    bill = get_object_or_404(
        Bill,
        pk=pk
    )

    # =================================================
    # GUARDAR INFORMACIÓN ANTES DE ELIMINAR
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
            "message": "Factura eliminada correctamente."
        },
        status=status.HTTP_200_OK
    )

