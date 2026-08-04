from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status

from .models import Bill
from .serializers import BillSerializer

from audit.services import create_audit


# ==========================================
# LISTAR FACTURAS
# ==========================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def bill_list(request):

    bills = Bill.objects.all().order_by('-created_at')

    serializer = BillSerializer(
        bills,
        many=True
    )

    return Response(
        serializer.data
    )


# ==========================================
# CREAR FACTURA
# ==========================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bill_create(request):

    serializer = BillSerializer(
        data=request.data
    )

    if serializer.is_valid():

        bill = serializer.save()

        # ==========================================
        # AUDITORÍA - CREAR FACTURA
        # ==========================================

        create_audit(

            user=request.user,

            action="create",

            module="billing",

            object_id=bill.id,

            description=(
                f"El usuario {request.user.username} "
                f"creó la factura con ID "
                f"{bill.id}."
            ),

            request=request

        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# ==========================================
# ACTUALIZAR FACTURA
# ==========================================

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def bill_update(request, pk):

    bill = get_object_or_404(
        Bill,
        pk=pk
    )

    serializer = BillSerializer(
        bill,
        data=request.data,
        partial=True
    )

    if serializer.is_valid():

        bill = serializer.save()

        # ==========================================
        # AUDITORÍA - ACTUALIZAR FACTURA
        # ==========================================

        create_audit(

            user=request.user,

            action="update",

            module="billing",

            object_id=bill.id,

            description=(
                f"El usuario {request.user.username} "
                f"actualizó la factura con ID "
                f"{bill.id}."
            ),

            request=request

        )

        return Response(
            serializer.data
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# ==========================================
# ELIMINAR FACTURA
# ==========================================

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def bill_delete(request, pk):

    bill = get_object_or_404(
        Bill,
        pk=pk
    )

    # ==========================================
    # GUARDAR ID ANTES DE ELIMINAR
    # ==========================================

    bill_id = bill.id

    # ==========================================
    # ELIMINAR FACTURA
    # ==========================================

    bill.delete()

    # ==========================================
    # AUDITORÍA - ELIMINAR FACTURA
    # ==========================================

    create_audit(

        user=request.user,

        action="delete",

        module="billing",

        object_id=bill_id,

        description=(
            f"El usuario {request.user.username} "
            f"eliminó la factura con ID "
            f"{bill_id}."
        ),

        request=request

    )

    return Response(

        {
            "message":
            "Factura eliminada"
        },

        status=status.HTTP_200_OK

    )