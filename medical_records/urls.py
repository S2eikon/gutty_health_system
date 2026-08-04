from django.urls import path

from .views import (
    medical_record_list,
    create_medical_record,
    update_medical_record,
    delete_medical_record,
)


# =====================================================
# URLS - HISTORIALES MÉDICOS
# =====================================================

urlpatterns = [

    # =================================================
    # LISTAR HISTORIALES
    # GET /medical-records/api/
    # =================================================

    path(
        'api/',
        medical_record_list,
        name='medical_record_list'
    ),

    # =================================================
    # CREAR HISTORIAL
    # POST /medical-records/api/create/
    # =================================================

    path(
        'api/create/',
        create_medical_record,
        name='create_medical_record'
    ),

    # =================================================
    # ACTUALIZAR HISTORIAL
    # PATCH /medical-records/api/<id>/
    # =================================================

    path(
        'api/<int:pk>/',
        update_medical_record,
        name='update_medical_record'
    ),

    # =================================================
    # ELIMINAR HISTORIAL
    # DELETE /medical-records/api/<id>/delete/
    # =================================================

    path(
        'api/<int:pk>/delete/',
        delete_medical_record,
        name='delete_medical_record'
    ),

]