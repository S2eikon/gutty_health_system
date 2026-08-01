from django.urls import path

from . import views



urlpatterns = [

    # ======================================================
    # LISTAR DOCUMENTOS
    # GET
    # /documents/api/
    # ======================================================

    path(
        "api/",
        views.documents_api,
        name="documents_api"
    ),



    # ======================================================
    # CREAR DOCUMENTO
    # POST multipart/form-data
    # /documents/api/create/
    #
    # Campos:
    # patient
    # title
    # document_type
    # description
    # file
    # ======================================================

    path(
        "api/create/",
        views.create_document_api,
        name="create_document"
    ),



    # ======================================================
    # DETALLE DOCUMENTO
    # GET
    # /documents/api/<id>/
    #
    # Ver información del documento
    # ======================================================

    path(
        "api/<int:document_id>/",
        views.document_detail_api,
        name="document_detail"
    ),



    # ======================================================
    # DESCARGAR DOCUMENTO
    # GET
    # /documents/api/<id>/download/
    #
    # Descarga física del archivo
    # ======================================================

    path(
        "api/<int:document_id>/download/",
        views.download_document_api,
        name="download_document"
    ),



    # ======================================================
    # ELIMINAR DOCUMENTO
    # DELETE
    # /documents/api/<id>/delete/
    # ======================================================

    path(
        "api/<int:document_id>/delete/",
        views.delete_document_api,
        name="delete_document"
    ),

]