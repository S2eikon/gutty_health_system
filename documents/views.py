from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import (
    api_view,
    permission_classes,
    parser_classes
)

from rest_framework.parsers import MultiPartParser, FormParser

from users.permissions import (
    IsAdmin,
    IsAdminDoctorPatientReceptionist,
)

from users.models import User

from .models import MedicalDocument
from .serializers import MedicalDocumentSerializer


# ======================================================
# LISTAR DOCUMENTOS
# ======================================================

@api_view(["GET"])
@permission_classes([IsAdminDoctorPatientReceptionist])
def documents_api(request):

    if request.user.role == "patient":

        documents = MedicalDocument.objects.filter(
            patient=request.user
        )

    else:

        documents = MedicalDocument.objects.all()


    serializer = MedicalDocumentSerializer(
        documents.order_by("-uploaded_at"),
        many=True
    )

    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )



# ======================================================
# SUBIR DOCUMENTO
# ======================================================

@api_view(["POST"])
@permission_classes([IsAdminDoctorPatientReceptionist])
@parser_classes([
    MultiPartParser,
    FormParser
])
def create_document_api(request):

    data = request.data.copy()


    # ------------------------------------------
    # Seguridad pacientes
    # ------------------------------------------

    if request.user.role == "patient":

        data["patient"] = request.user.id



    # ------------------------------------------
    # Validar paciente
    # ------------------------------------------

    patient_id = data.get("patient")


    if not patient_id:

        return Response(
            {
                "error": "Debe especificar el paciente."
            },
            status=status.HTTP_400_BAD_REQUEST
        )


    patient = get_object_or_404(
        User,
        id=patient_id
    )


    serializer = MedicalDocumentSerializer(
        data=data
    )


    if serializer.is_valid():

        serializer.save(
            uploaded_by=request.user,
            patient=patient
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
# DESCARGAR DOCUMENTO
# ======================================================

@api_view(["GET"])
@permission_classes([IsAdminDoctorPatientReceptionist])
def download_document_api(request, document_id):

    if request.user.role == "patient":

        document = get_object_or_404(
            MedicalDocument,
            id=document_id,
            patient=request.user
        )

    else:

        document = get_object_or_404(
            MedicalDocument,
            id=document_id
        )


    if not document.file:

        raise Http404(
            "El documento no tiene archivo asociado."
        )


    return FileResponse(
        document.file.open("rb"),
        as_attachment=True,
        filename=document.file.name.split("/")[-1]
    )



# ======================================================
# DETALLE DOCUMENTO
# ======================================================

@api_view(["GET"])
@permission_classes([IsAdminDoctorPatientReceptionist])
def document_detail_api(request, document_id):


    if request.user.role == "patient":

        document = get_object_or_404(
            MedicalDocument,
            id=document_id,
            patient=request.user
        )


    else:

        document = get_object_or_404(
            MedicalDocument,
            id=document_id
        )


    serializer = MedicalDocumentSerializer(
        document
    )


    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )



# ======================================================
# ELIMINAR DOCUMENTO
# ======================================================

@api_view(["DELETE"])
@permission_classes([IsAdmin])
def delete_document_api(request, document_id):


    document = get_object_or_404(
        MedicalDocument,
        id=document_id
    )


    if document.file:

        document.file.delete(
            save=False
        )


    document.delete()


    return Response(
        {
            "message": "Documento eliminado correctamente."
        },
        status=status.HTTP_200_OK
    )