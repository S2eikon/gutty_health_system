from django.urls import path
from . import views
from . import api_views  

urlpatterns = [

    # =========================
    # 🔌 API PARA ANGULAR
    # =========================

    # 📥 LISTAR CITAS
    path('api/', views.appointments_api, name='appointments_api'),

    # ➕ CREAR CITA
    path('api/create/', api_views.api_create_appointment, name='api_create_appointment'),

    # ❌ DETALLE / ELIMINAR CITA
    path('api/<int:appointment_id>/', views.appointment_detail_api, name='appointment_detail_api'),
]