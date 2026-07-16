from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

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

    def __str__(self):
        return f"{self.username} ({self.role})"