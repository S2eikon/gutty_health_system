from django.urls import path

from .views import (
    medical_record_list,
    create_medical_record,
    update_medical_record,
    delete_medical_record,
)

urlpatterns = [

    path(
        'api/',
        medical_record_list,
        name='medical_record_list'
    ),

    path(
        'api/create/',
        create_medical_record,
        name='create_medical_record'
    ),

    path(
        'api/<int:pk>/',
        update_medical_record,
        name='update_medical_record'
    ),

    path(
        'api/<int:pk>/delete/',
        delete_medical_record,
        name='delete_medical_record'
    ),

]