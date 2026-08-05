from django.urls import path

from . import views


urlpatterns = [

    # =====================================================
    # LISTAR FACTURAS
    # =====================================================

    path(
        'api/',
        views.bill_list
    ),

    # =====================================================
    # CREAR FACTURA
    # =====================================================

    path(
        'api/create/',
        views.bill_create
    ),

    # =====================================================
    # ACTUALIZAR FACTURA
    # =====================================================

    path(
        'api/<int:pk>/',
        views.bill_update
    ),

    # =====================================================
    # ELIMINAR FACTURA
    # =====================================================

    path(
        'api/<int:pk>/delete/',
        views.bill_delete
    ),
]

