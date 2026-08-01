from django.urls import path

from . import views


urlpatterns = [

    # ==========================================
    # LISTAR AUDITORÍA
    # GET /audit/api/
    # ==========================================

    path(

        "api/",

        views.audit_logs_api,

        name="audit_logs_api"

    ),



    # ==========================================
    # CREAR REGISTRO DE AUDITORÍA
    # POST /audit/api/create/
    # ==========================================

    path(

        "api/create/",

        views.create_audit_api,

        name="create_audit_api"

    ),

]