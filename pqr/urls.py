from django.urls import path

from . import views


# =====================================================
# RUTAS DEL MÓDULO PQR
# =====================================================

urlpatterns = [

    # =================================================
    # LISTAR PQR
    # GET /pqr/api/
    # =================================================

    path(
        "api/",
        views.pqr_api,
        name="pqr_api"
    ),

    # =================================================
    # CREAR PQR
    # POST /pqr/api/create/
    # =================================================

    path(
        "api/create/",
        views.create_pqr_api,
        name="create_pqr"
    ),

    # =================================================
    # DETALLE PQR
    # GET /pqr/api/<id>/
    # =================================================

    path(
        "api/<int:pqr_id>/",
        views.pqr_detail_api,
        name="pqr_detail"
    ),

    # =================================================
    # RESPONDER PQR
    # PUT /pqr/api/<id>/respond/
    # =================================================

    path(
        "api/<int:pqr_id>/respond/",
        views.respond_pqr_api,
        name="respond_pqr"
    ),

    # =================================================
    # ELIMINAR PQR
    # DELETE /pqr/api/<id>/delete/
    # =================================================

    path(
        "api/<int:pqr_id>/delete/",
        views.delete_pqr_api,
        name="delete_pqr"
    ),
]
