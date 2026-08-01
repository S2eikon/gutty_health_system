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


# ======================================================
# LISTAR PQR
# ======================================================

@api_view(["GET"])
@permission_classes([IsAdminDoctorPatientReceptionist])
def pqr_api(request):

    if request.user.role == "patient":

        pqrs = PQR.objects.filter(
            user=request.user
        )

    else:

        pqrs = PQR.objects.all()

    serializer = PQRSerializer(
        pqrs.order_by("-created_at"),
        many=True
    )

    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )


# ======================================================
# CREAR PQR
# ======================================================

@api_view(["POST"])
@permission_classes([IsAdminDoctorPatientReceptionist])
def create_pqr_api(request):

    serializer = PQRSerializer(
        data=request.data
    )

    if serializer.is_valid():

        serializer.save(
            user=request.user,
            status="open"
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# ======================================================
# DETALLE PQR
# ======================================================

@api_view(["GET"])
@permission_classes([IsAdminDoctorPatientReceptionist])
def pqr_detail_api(request, pqr_id):

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

    serializer = PQRSerializer(pqr)

    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )


# ======================================================
# RESPONDER PQR
# ======================================================

@api_view(["PUT"])
@permission_classes([IsAdmin])
def respond_pqr_api(request, pqr_id):

    pqr = get_object_or_404(
        PQR,
        id=pqr_id
    )

    response_text = request.data.get("response")

    if not response_text:

        return Response(
            {
                "error": "La respuesta es obligatoria."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    pqr.response = response_text

    pqr.status = request.data.get(
        "status",
        "in_progress"
    )

    pqr.responded_by = request.user

    pqr.responded_at = timezone.now()

    pqr.save()

    serializer = PQRSerializer(pqr)

    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )


# ======================================================
# ELIMINAR PQR
# ======================================================

@api_view(["DELETE"])
@permission_classes([IsAdmin])
def delete_pqr_api(request, pqr_id):

    pqr = get_object_or_404(
        PQR,
        id=pqr_id
    )

    pqr.delete()

    return Response(
        {
            "message": "PQR eliminada correctamente."
        },
        status=status.HTTP_200_OK
    )