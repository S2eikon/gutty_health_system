from django.urls import path

from .views import (
    register_view,
    login_view,
    logout_view,
    ProfileAPIView,
    patient_list_api,  # Importar la nueva vista
)

urlpatterns = [

    # HTML
    path(
        'register/',
        register_view,
        name='register'
    ),

    path(
        'login/',
        login_view,
        name='login'
    ),

    path(
        'logout/',
        logout_view,
        name='logout'
    ),

    # API REST
    path(
        'profile/',
        ProfileAPIView.as_view(),
        name='profile'
    ),

    # Nueva ruta para obtener lista de pacientes
    path(
        'api/patients/',
        patient_list_api,
        name='patient_list_api'
    ),

]
