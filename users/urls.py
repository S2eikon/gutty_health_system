from django.urls import path

from .views import (
    register_view,
    login_view,
    logout_view,
    ProfileAPIView,
    patient_list_api,
    register_api,
)


# =====================================================
# URLS - USUARIOS
# =====================================================

urlpatterns = [

    # =================================================
    # AUTENTICACIÓN HTML
    # =================================================

    path(
        "register/",
        register_view,
        name="register"
    ),

    path(
        "login/",
        login_view,
        name="login"
    ),

    path(
        "logout/",
        logout_view,
        name="logout"
    ),

    # =================================================
    # API REST - REGISTRO DE USUARIO
    # =================================================

    # POST /users/api/register/
    #
    # Esta ruta es utilizada por Angular para registrar
    # nuevos usuarios.
    #
    # La auditoría del registro se realiza dentro
    # de register_api.

    path(
        "api/register/",
        register_api,
        name="register_api"
    ),

    # =================================================
    # API REST - PERFIL
    # =================================================

    # GET /users/api/profile/
    # PUT /users/api/profile/
    #
    # La auditoría de consulta y actualización
    # se realiza dentro de ProfileAPIView.

    path(
        "api/profile/",
        ProfileAPIView.as_view(),
        name="profile"
    ),

    # =================================================
    # API REST - PACIENTES
    # =================================================

    # GET /users/api/patients/
    #
    # La auditoría de consulta y acceso no autorizado
    # se realiza dentro de patient_list_api.

    path(
        "api/patients/",
        patient_list_api,
        name="patient_list_api"
    ),

]