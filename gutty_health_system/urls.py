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

from django.urls import (
    path,
    include
)

from django.http import HttpResponse

from django.conf import settings

from django.conf.urls.static import static


from rest_framework_simplejwt.views import (

    TokenObtainPairView,

    TokenRefreshView

)





# =========================
# 🏠 HOME
# =========================

def home(request):

    return HttpResponse(
        "Sistema Clínico Gutty funcionando 🚀"
    )







# =========================
# 🌐 URLS PRINCIPALES
# =========================

urlpatterns = [



    # =====================
    # HOME
    # =====================

    path(
        '',
        home
    ),





    # =====================
    # ADMIN DJANGO
    # =====================

    path(
        'admin/',
        admin.site.urls
    ),





    # =====================
    # 👤 USUARIOS
    # =====================

    path(
        'users/',
        include('users.urls')
    ),





    # =====================
    # 📅 CITAS
    # =====================

    path(
        'appointments/',
        include('appointments.urls')
    ),





    # =====================
    # 📊 DASHBOARD
    # =====================

    path(
        'dashboard/',
        include('dashboard.urls')
    ),





    # =====================
    # 🏥 HISTORIAS CLÍNICAS
    # =====================

    path(
        'medical-records/',
        include('medical_records.urls')
    ),





    # =====================
    # 📄 DOCUMENTOS MÉDICOS
    # =====================

    path(
        'documents/',
        include('documents.urls')
    ),





    # =====================
    # 💳 FACTURACIÓN
    # =====================

    path(
        'billing/',
        include('billing.urls')
    ),





    # =====================
    # 🔐 JWT LOGIN
    # =====================

    path(

        'api/token/',

        TokenObtainPairView.as_view(),

        name='token_obtain_pair'

    ),




    # =====================
    # 🔄 JWT REFRESH
    # =====================

    path(

        'api/token/refresh/',

        TokenRefreshView.as_view(),

        name='token_refresh'

    ),


]

# =========================
# 📂 ARCHIVOS MEDIA
# Desarrollo solamente
# =========================

if settings.DEBUG:


    urlpatterns += static(

        settings.MEDIA_URL,

        document_root=settings.MEDIA_ROOT

    )

