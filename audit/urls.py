from django.urls import path

from . import views


# =====================================================
# URLS DEL MÓDULO DE AUDITORÍA
# =====================================================

urlpatterns = [

    # =================================================
    # LISTAR REGISTROS DE AUDITORÍA
    #
    # GET:
    # /audit/api/
    #
    # Filtros disponibles:
    #
    # /audit/api/?module=billing
    # /audit/api/?action=denied
    # /audit/api/?user=ruben
    #
    # Acceso controlado desde views.py
    # =================================================

    path(
        "api/",
        views.audit_logs_api,
        name="audit_logs_api"
    ),


    # =================================================
    # CREAR REGISTRO DE AUDITORÍA
    #
    # POST:
    # /audit/api/create/
    #
    # Acceso controlado desde views.py
    # =================================================

    path(
        "api/create/",
        views.create_audit_api,
        name="create_audit_api"
    ),

]

