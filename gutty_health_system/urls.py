"""
URL configuration for gutty_health_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

# =========================
# 🏠 HOME
# =========================
def home(request):
    return HttpResponse("Sistema Clínico Gutty funcionando 🚀")


urlpatterns = [

    # =========================
    # 🏠 ROOT
    # =========================
    path('', home),

    # =========================
    # ⚙️ ADMIN
    # =========================
    path('admin/', admin.site.urls),

    # =========================
    # 👤 APPS
    # =========================
    path('users/', include('users.urls')),
    path('appointments/', include('appointments.urls')),
    path('dashboard/', include('dashboard.urls')),

    # Aquí agregamos la ruta para medical_records
    path('medical-records/', include('medical_records.urls')),

    # =========================
    # 🔐 JWT
    # =========================
    path(
        'api/token/',
        TokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),

    path(
        'api/token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'
    ),

]
