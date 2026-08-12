from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    # =====================================================
    # ROLES
    # =====================================================

    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('doctor', 'Doctor'),
        ('patient', 'Paciente'),
        ('receptionist', 'Recepcionista'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='patient'
    )

    # =====================================================
    # CELULAR
    # =====================================================

    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    # =====================================================
    # REPRESENTACIÓN
    # =====================================================

    def __str__(self):
        return f"{self.username} ({self.role})"