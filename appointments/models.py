from django.db import models
from users.models import User
from django.core.exceptions import ValidationError


class Appointment(models.Model):

    # =========================
    # 🏥 TIPOS DE CITA
    # =========================
    TYPE_CHOICES = [
        ('first', 'Primera cita'),
        ('control', 'Control'),
        ('followup', 'Seguimiento'),
        ('delivery', 'Entrega medicamentos'),
        ('spa', 'Spa'),
        ('cosmetic', 'Limpieza facial'),
    ]

    # =========================
    # 📌 ESTADOS
    # =========================
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmada'),
        ('cancelled', 'Cancelada'),
        ('rescheduled', 'Reprogramada'),
    ]

    # =========================
    # 👤 PACIENTE
    # =========================
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='appointments_as_patient'
    )

    # =========================
    # 👨‍⚕️ DOCTOR
    # =========================
    doctor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='appointments_as_doctor'
    )

    # =========================
    # 📅 DATOS CITA
    # =========================
    appointment_type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES
    )

    date = models.DateField()

    time = models.TimeField()

    # =========================
    # 📌 ESTADO
    # =========================
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # =========================
    # 🕒 FECHA CREACIÓN
    # =========================
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    # =========================
    # 🔥 VALIDACIÓN HORARIO
    # =========================
    def clean(self):

        # Solo citas entre 1PM y 7PM
        if self.time.hour < 13 or self.time.hour >= 19:
            raise ValidationError(
                "Las citas solo se permiten de 1PM a 7PM"
            )

    # =========================
    # 💾 SAVE
    # =========================
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    # =========================
    # 🏷️ TEXTO ADMIN
    # =========================
    def __str__(self):
        return f"{self.patient} - {self.get_appointment_type_display()} - {self.date}"