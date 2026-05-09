from django.db import models
from users.models import User
from django.core.exceptions import ValidationError


class Appointment(models.Model):

    TYPE_CHOICES = [
        ('first', 'Primera cita dermatología'),
        ('control', 'Control dermatológico'),
        ('followup', 'Seguimiento tratamiento'),
        ('delivery', 'Entrega medicamentos'),
        ('spa', 'Spa Natural Gutty'),
        ('cosmetic', 'Limpieza facial'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmada'),
        ('cancelled', 'Cancelada'),
        ('rescheduled', 'Reprogramada'),
    ]

    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='appointments_as_patient'
    )

    doctor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='appointments_as_doctor'
    )

    appointment_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    date = models.DateField()
    time = models.TimeField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.time.hour < 13 or self.time.hour >= 19:
            raise ValidationError("Las citas solo se permiten de 1PM a 7PM")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)