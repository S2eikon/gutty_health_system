from django.urls import path
from . import views

urlpatterns = [
    path('api/', views.bill_list),
    path('api/create/', views.bill_create),
    path('api/<int:pk>/', views.bill_update),
    path('api/<int:pk>/delete/', views.bill_delete),
]
