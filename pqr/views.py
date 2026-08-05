from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from users.permissions import (
    IsAdmin,
    IsAdminDoctorPatientReceptionist,
)

from .models import PQR
from .serializers import PQRSerializer

from audit.services import create_audit


# =====================================================
# LISTAR PQR
# =====================================================

@api_view(["GET"])
@permission_classes([IsAdminDoctorPatientReceptionist])
def pqr_api(request):

    # =================================================
    # OBTENER PQR SEGÚN EL ROL
    # =================================================

    if request.user.role == "patient":

        pqrs = PQR.objects.filter(
            user=request.user
        )

    else:

        pqrs = PQR.objects.all()

    # =================================================
    # SERIALIZAR INFORMACIÓN
    # =================================================

    serializer = PQRSerializer(
        pqrs.order_by("-created_at"),
        many=True
    )

    # =================================================
    # AUDITORÍA - CONSULTAR PQR
    # =================================================

    create_audit(
        user=request.user,
        action="read",
        module="pqr",
        object_id=None,
        description=(
            f"El usuario {request.user.username} "
            f"consultó la lista de PQR."
        ),
        request=request
    )

    # =================================================
    # RESPUESTA
    # =================================================

    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )


# =====================================================
# CREAR PQR
# =====================================================

@api_view(["POST"])
@permission_classes([IsAdminDoctorPatientReceptionist])
def create_pqr_api(request):

    serializer = PQRSerializer(
        data=request.data
    )

    # =================================================
    # VALIDAR INFORMACIÓN
    # =================================================

    if serializer.is_valid():

        # =============================================
        # CREAR PQR
        # =============================================

        pqr = serializer.save(
            user=request.user,
            status="open"
        )

        # =============================================
        # AUDITORÍA - CREAR PQR
        # =============================================

        create_audit(
            user=request.user,
            action="create",
            module="pqr",
            object_id=pqr.id,
            description=(
                f"El usuario {request.user.username} "
                f"creó la PQR con ID {pqr.id}."
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
# DETALLE PQR
# =====================================================

@api_view(["GET"])
@permission_classes([IsAdminDoctorPatientReceptionist])
def pqr_detail_api(request, pqr_id):

    # =================================================
    # BUSCAR PQR SEGÚN EL ROL
    # =================================================

    if request.user.role == "patient":

        pqr = get_object_or_404(
            PQR,
            id=pqr_id,
            user=request.user
        )

    else:

        pqr = get_object_or_404(
            PQR,
            id=pqr_id
        )

    # =================================================
    # SERIALIZAR
    # =================================================

    serializer = PQRSerializer(
        pqr
    )

    # =================================================
    # AUDITORÍA - CONSULTAR DETALLE
    # =================================================

    create_audit(
        user=request.user,
        action="read",
        module="pqr",
        object_id=pqr.id,
        description=(
            f"El usuario {request.user.username} "
            f"consultó el detalle de la PQR "
            f"con ID {pqr.id}."
        ),
        request=request
    )

    # =================================================
    # RESPUESTA
    # =================================================

    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )


# =====================================================
# RESPONDER PQR
# =====================================================

@api_view(["PUT"])
@permission_classes([IsAdmin])
def respond_pqr_api(request, pqr_id):

    # =================================================
    # BUSCAR PQR
    # =================================================

    pqr = get_object_or_404(
        PQR,
        id=pqr_id
    )

    # =================================================
    # OBTENER RESPUESTA
    # =================================================

    response_text = request.data.get(
        "response"
    )

    # =================================================
    # VALIDAR RESPUESTA
    # =================================================

    if not response_text:

        return Response(
            {
                "error":
                "La respuesta es obligatoria."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # =================================================
    # ACTUALIZAR PQR
    # =================================================

    pqr.response = response_text

    pqr.status = request.data.get(
        "status",
        "in_progress"
    )

    pqr.responded_by = request.user

    pqr.responded_at = timezone.now()

    pqr.save()

    # =================================================
    # AUDITORÍA - ACTUALIZAR PQR
    # =================================================

    create_audit(
        user=request.user,
        action="update",
        module="pqr",
        object_id=pqr.id,
        description=(
            f"El usuario {request.user.username} "
            f"respondió y actualizó la PQR "
            f"con ID {pqr.id}."
        ),
        request=request
    )

    # =================================================
    # SERIALIZAR
    # =================================================

    serializer = PQRSerializer(
        pqr
    )

    # =================================================
    # RESPUESTA
    # =================================================

    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )


# =====================================================
# ELIMINAR PQR
# =====================================================

@api_view(["DELETE"])
@permission_classes([IsAdmin])
def delete_pqr_api(request, pqr_id):

    # =================================================
    # BUSCAR PQR
    # =================================================

    pqr = get_object_or_404(
        PQR,
        id=pqr_id
    )

    # =================================================
    # GUARDAR ID ANTES DE ELIMINAR
    # =================================================

    pqr_id_deleted = pqr.id

    # =================================================
    # AUDITORÍA - ELIMINAR PQR
    # =================================================

    create_audit(
        user=request.user,
        action="delete",
        module="pqr",
        object_id=pqr_id_deleted,
        description=(
            f"El usuario {request.user.username} "
            f"eliminó la PQR con ID "
            f"{pqr_id_deleted}."
        ),
        request=request
    )

    # =================================================
    # ELIMINAR PQR
    # =================================================

    pqr.delete()

    # =================================================
    # RESPUESTA
    # =================================================

    return Response(
        {
            "message":
            "PQR eliminada correctamente."
        },
        status=status.HTTP_200_OK
    )

