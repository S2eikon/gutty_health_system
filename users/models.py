# ======================================================
# USERS / MODELS.PY
# GUTTY HEALTH SYSTEM
# ======================================================

from django.contrib.auth.models import AbstractUser
from django.db import models


# ======================================================
# MODELO DE USUARIO
# ======================================================

class User(AbstractUser):

    # ==================================================
    # ROLES DEL SISTEMA
    # ==================================================

    ROLE_CHOICES = [

        (
            'admin',
            'Administrador'
        ),

        (
            'doctor',
            'Doctor'
        ),

        (
            'patient',
            'Paciente'
        ),

        (
            'receptionist',
            'Recepcionista'
        ),

        (
            'esthetician',
            'Esteticista'
        ),

    ]


    role = models.CharField(

        max_length=20,

        choices=ROLE_CHOICES,

        default='patient'

    )


    # ==================================================
    # CELULAR
    # ==================================================

    phone = models.CharField(

        max_length=20,

        blank=True,

        null=True

    )


    # ==================================================
    # REPRESENTACIÓN
    # ==================================================

    def __str__(self):

        return (
            f"{self.username} ({self.role})"
        )