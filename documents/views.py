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
# PAGINACIÓN DE DOCUMENTOS
# =====================================================

from rest_framework.pagination import PageNumberPagination


class DocumentPagination(PageNumberPagination):
    """
    Paginación para documentos médicos.

    Por defecto:
    - 5 documentos por página.

    El cliente puede solicitar otra cantidad mediante:
    ?page_size=10

    Se limita a un máximo de 20 documentos por página.
    """

    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 20


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

        # =============================================
        # FILTRAR POR PACIENTE
        # =============================================

        patient_id = request.query_params.get("patient")

        if patient_id:

            documents = documents.filter(
                patient_id=patient_id
            )

    # =================================================
    # PAGINACIÓN
    # =================================================

    paginator = DocumentPagination()

    page = paginator.paginate_queryset(
        documents,
        request
    )

    serializer = MedicalDocumentSerializer(
        page,
        many=True,
        context={
            "request": request
        }
    )

    # =================================================
    # AUDITORÍA
    # =================================================

    create_audit(

        user=request.user,

        action="read",

        module="documents",

        object_id=None,

        description=(
            f"El usuario {request.user.username} "
            f"consultó la lista de documentos médicos. "
            f"Página {request.query_params.get('page', '1')}."
        ),

        request=request
    )

    # =================================================
    # RESPUESTA PAGINADA
    # =================================================

    return paginator.get_paginated_response(
        serializer.data
    )


# =====================================================
# SUBIR / CREAR DOCUMENTO
# =====================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_document_api(request):

    serializer = MedicalDocumentSerializer(
        data=request.data
    )

    if serializer.is_valid():

        document = serializer.save(
            uploaded_by=request.user
        )

        # =================================================
        # AUDITORÍA
        # =================================================

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

        return Response(

            {
                "message":
                "Documento subido correctamente.",

                "document":
                MedicalDocumentSerializer(
                    document,
                    context={
                        "request": request
                    }
                ).data
            },

            status=status.HTTP_201_CREATED
        )

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

    document = get_object_or_404(
        MedicalDocument,
        id=document_id
    )

    # =================================================
    # SEGURIDAD
    # =================================================

    if request.user.role == "patient":

        if document.patient_id != request.user.id:

            create_audit(

                user=request.user,

                action="denied",

                module="documents",

                object_id=document.id,

                description=(
                    f"El usuario {request.user.username} "
                    f"intentó consultar el documento "
                    f"'{document.title}' "
                    f"con ID {document.id} "
                    f"sin permisos."
                ),

                request=request
            )

            return Response(

                {
                    "detail":
                    "No tiene permisos para consultar este documento."
                },

                status=status.HTTP_403_FORBIDDEN
            )

    serializer = MedicalDocumentSerializer(

        document,

        context={
            "request": request
        }

    )

    # =================================================
    # AUDITORÍA
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

    return Response(

        serializer.data,

        status=status.HTTP_200_OK
    )


# =====================================================
# DESCARGAR / VISUALIZAR DOCUMENTO
# =====================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def download_document_api(request, document_id):

    document = get_object_or_404(
        MedicalDocument,
        id=document_id
    )

    # =================================================
    # SEGURIDAD
    # =================================================

    if request.user.role == "patient":

        if document.patient_id != request.user.id:

            create_audit(

                user=request.user,

                action="denied",

                module="documents",

                object_id=document.id,

                description=(
                    f"El usuario {request.user.username} "
                    f"intentó acceder al archivo del documento "
                    f"'{document.title}' "
                    f"con ID {document.id} "
                    f"sin permisos."
                ),

                request=request
            )

            return Response(

                {
                    "detail":
                    "No tiene permisos para acceder a este documento."
                },

                status=status.HTTP_403_FORBIDDEN
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
    # AUDITORÍA
    # =================================================

    create_audit(

        user=request.user,

        action="download",

        module="documents",

        object_id=document.id,

        description=(
            f"El usuario {request.user.username} "
            f"accedió al archivo del documento "
            f"'{document.title}' "
            f"con ID {document.id}."
        ),

        request=request
    )

    # =================================================
    # ABRIR ARCHIVO EN EL NAVEGADOR
    # =================================================

    try:

        file_handle = document.file.open("rb")

        response = FileResponse(

            file_handle,

            as_attachment=False,

            filename=document.file.name.split("/")[-1]

        )

        # =================================================
        # IMPORTANTE:
        # INLINE permite visualizar PDF/JPG/PNG
        # directamente en el navegador.
        # =================================================

        response["Content-Disposition"] = (
            f'inline; filename="{document.file.name.split("/")[-1]}"'
        )

        # =================================================
        # DETECTAR TIPO DE ARCHIVO
        # =================================================

        file_name = document.file.name.lower()

        if file_name.endswith(".pdf"):

            response["Content-Type"] = "application/pdf"

        elif file_name.endswith(".jpg") or file_name.endswith(".jpeg"):

            response["Content-Type"] = "image/jpeg"

        elif file_name.endswith(".png"):

            response["Content-Type"] = "image/png"

        elif file_name.endswith(".gif"):

            response["Content-Type"] = "image/gif"

        elif file_name.endswith(".webp"):

            response["Content-Type"] = "image/webp"

        else:

            response["Content-Type"] = "application/octet-stream"

        return response

    except FileNotFoundError:

        return Response(

            {
                "error":
                "El archivo físico no existe en el servidor."
            },

            status=status.HTTP_404_NOT_FOUND
        )


# =====================================================
# ELIMINAR DOCUMENTO
# =====================================================

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_document_api(request, document_id):

    document = get_object_or_404(
        MedicalDocument,
        id=document_id
    )

    # =================================================
    # SEGURIDAD
    # =================================================

    if request.user.role == "patient":

        if document.patient_id != request.user.id:

            create_audit(

                user=request.user,

                action="denied",

                module="documents",

                object_id=document.id,

                description=(
                    f"El usuario {request.user.username} "
                    f"intentó eliminar el documento "
                    f"'{document.title}' "
                    f"con ID {document.id} "
                    f"sin permisos."
                ),

                request=request
            )

            return Response(

                {
                    "detail":
                    "No tiene permisos para eliminar este documento."
                },

                status=status.HTTP_403_FORBIDDEN
            )

    # =================================================
    # GUARDAR INFORMACIÓN
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
    # ELIMINAR REGISTRO
    # =================================================

    document.delete()

    # =================================================
    # AUDITORÍA
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

    return Response(

        {
            "message":
            "Documento eliminado correctamente."
        },

        status=status.HTTP_200_OK
    )
