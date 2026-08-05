from django.shortcuts import get_object_or_404
from django.http import FileResponse

from rest_framework.decorators import (
    api_view,
    permission_classes
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import MedicalDocument
from .serializers import MedicalDocumentSerializer

from audit.services import create_audit


# =====================================================
# LISTAR DOCUMENTOS
# =====================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def documents_api(request):

    # =================================================
    # OBTENER DOCUMENTOS
    # =================================================

    if request.user.role == "patient":

        documents = MedicalDocument.objects.filter(
            patient=request.user
        ).order_by("-uploaded_at")

    else:

        documents = MedicalDocument.objects.all().order_by(
            "-uploaded_at"
        )

    serializer = MedicalDocumentSerializer(
        documents,
        many=True
    )

    # =================================================
    # AUDITORÍA - CONSULTAR DOCUMENTOS
    # =================================================

    create_audit(

        user=request.user,

        action="read",

        module="documents",

        object_id=None,

        description=(
            f"El usuario {request.user.username} "
            f"consultó la lista de documentos médicos."
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
# SUBIR / CREAR DOCUMENTO
# =====================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_document_api(request):

    # =================================================
    # VALIDAR INFORMACIÓN
    # =================================================

    serializer = MedicalDocumentSerializer(
        data=request.data
    )

    if serializer.is_valid():

        # =============================================
        # GUARDAR DOCUMENTO
        # =============================================

        document = serializer.save(
            uploaded_by=request.user
        )

        # =============================================
        # AUDITORÍA - CREAR DOCUMENTO
        # =============================================

        create_audit(

            user=request.user,

            action="upload",

            module="documents",

            object_id=document.id,

            description=(
                f"El usuario {request.user.username} "
                f"subió el documento "
                f"'{document.title}' "
                f"con ID {document.id}."
            ),

            request=request
        )

        # =============================================
        # RESPUESTA
        # =============================================

        return Response(

            {
                "message":
                "Documento subido correctamente.",

                "document":
                MedicalDocumentSerializer(
                    document
                ).data
            },

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
# DETALLE DE DOCUMENTO
# =====================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def document_detail_api(request, document_id):

    # =================================================
    # BUSCAR DOCUMENTO
    # =================================================

    document = get_object_or_404(
        MedicalDocument,
        id=document_id
    )

    # =================================================
    # SERIALIZAR
    # =================================================

    serializer = MedicalDocumentSerializer(
        document
    )

    # =================================================
    # AUDITORÍA - CONSULTAR DETALLE
    # =================================================

    create_audit(

        user=request.user,

        action="read",

        module="documents",

        object_id=document.id,

        description=(
            f"El usuario {request.user.username} "
            f"consultó el documento "
            f"'{document.title}' "
            f"con ID {document.id}."
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
# DESCARGAR DOCUMENTO
# =====================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def download_document_api(request, document_id):

    # =================================================
    # BUSCAR DOCUMENTO
    # =================================================

    document = get_object_or_404(
        MedicalDocument,
        id=document_id
    )

    # =================================================
    # VERIFICAR ARCHIVO
    # =================================================

    if not document.file:

        return Response(

            {
                "error":
                "El documento no tiene un archivo asociado."
            },

            status=status.HTTP_404_NOT_FOUND
        )

    # =================================================
    # AUDITORÍA - DESCARGAR DOCUMENTO
    # =================================================

    create_audit(

        user=request.user,

        action="download",

        module="documents",

        object_id=document.id,

        description=(
            f"El usuario {request.user.username} "
            f"descargó el documento "
            f"'{document.title}' "
            f"con ID {document.id}."
        ),

        request=request
    )

    # =================================================
    # RESPUESTA DE ARCHIVO
    # =================================================

    try:

        response = FileResponse(
            document.file.open("rb"),
            as_attachment=True,
            filename=document.file.name.split("/")[-1]
        )

        return response

    except FileNotFoundError:

        return Response(

            {
                "error":
                "El archivo físico no existe."
            },

            status=status.HTTP_404_NOT_FOUND
        )


# =====================================================
# ELIMINAR DOCUMENTO
# =====================================================

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_document_api(request, document_id):

    # =================================================
    # BUSCAR DOCUMENTO
    # =================================================

    document = get_object_or_404(
        MedicalDocument,
        id=document_id
    )

    # =================================================
    # GUARDAR INFORMACIÓN ANTES DE ELIMINAR
    # =================================================

    document_id_value = document.id
    document_title = document.title

    # =================================================
    # ELIMINAR ARCHIVO FÍSICO
    # =================================================

    if document.file:

        try:

            document.file.delete(
                save=False
            )

        except PermissionError:

            return Response(

                {
                    "error": (
                        "No se pudo eliminar el archivo "
                        "porque está siendo utilizado "
                        "por otro proceso."
                    )
                },

                status=status.HTTP_409_CONFLICT
            )

    # =================================================
    # ELIMINAR REGISTRO DE BASE DE DATOS
    # =================================================

    document.delete()

    # =================================================
    # AUDITORÍA - ELIMINAR DOCUMENTO
    # =================================================

    create_audit(

        user=request.user,

        action="delete",

        module="documents",

        object_id=document_id_value,

        description=(
            f"El usuario {request.user.username} "
            f"eliminó el documento "
            f"'{document_title}' "
            f"con ID {document_id_value}."
        ),

        request=request
    )

    # =================================================
    # RESPUESTA
    # =================================================

    return Response(

        {
            "message":
            "Documento eliminado correctamente."
        },

        status=status.HTTP_200_OK
    )