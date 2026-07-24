from django.urls import path
from .views import citas_por_estado

urlpatterns = [
    path('citas-por-estado/', citas_por_estado, name='citas_por_estado'),
]
