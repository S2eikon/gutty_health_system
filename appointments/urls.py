from django.urls import path
from . import views
from . import api_views

urlpatterns = [

    # 📥 LISTAR
    path(
        'api/',
        views.appointments_api,
        name='appointments_api'
    ),

    # ➕ CREAR
    path(
        'api/create/',
        api_views.api_create_appointment,
        name='api_create_appointment'
    ),

    # ❌ ELIMINAR
    path(
        'api/<int:appointment_id>/',
        views.appointment_detail_api,
        name='appointment_detail_api'
    ),

    # 🔄 CAMBIAR ESTADO
    path(
        'api/<int:appointment_id>/status/',
        views.update_appointment_status,
        name='update_appointment_status'
    ),
]