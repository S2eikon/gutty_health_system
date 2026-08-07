from django.db import models
from django.core.exceptions import ValidationError

from users.models import User


class Appointment(models.Model):

    # ======================================================
    # TIPOS DE CITA
    # ======================================================

    TYPE_CHOICES = [
        (
            'first',
            'Primera cita dermatología'
        ),
        (
            'control',
            'Control dermatológico'
        ),
        (
            'followup',
            'Seguimiento tratamiento'
        ),
        (
            'delivery',
            'Entrega medicamentos'
        ),
        (
            'spa',
            'Spa Natural Gutty'
        ),
        (
            'cosmetic',
            'Limpieza facial'
        ),
    ]


    # ======================================================
    # ESTADOS DE LA CITA
    # ======================================================

    STATUS_CHOICES = [
        (
            'pending',
            'Pendiente'
        ),
        (
            'confirmed',
            'Confirmada'
        ),
        (
            'cancelled',
            'Cancelada'
        ),
        (
            'rescheduled',
            'Reprogramada'
        ),
    ]


    # ======================================================
    # PACIENTE
    # ======================================================

    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='appointments_as_patient'
    )


    # ======================================================
    # DOCTOR
    # ======================================================

    doctor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='appointments_as_doctor'
    )


    # ======================================================
    # TIPO DE CITA
    # ======================================================

    appointment_type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES
    )


    # ======================================================
    # FECHA
    # ======================================================

    date = models.DateField()


    # ======================================================
    # HORA
    # ======================================================

    time = models.TimeField()


    # ======================================================
    # ESTADO
    # ======================================================

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )


    # ======================================================
    # FECHA DE CREACIÓN
    # ======================================================

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    # ======================================================
    # RECORDATORIOS
    #
    # IMPORTANTE:
    #
    # Estos campos corresponden a recordatorios enviados
    # por correo y son independientes de las notificaciones
    # de eventos de la cita.
    # ======================================================

    reminder_sent = models.BooleanField(
        default=False
    )

    reminder_sent_at = models.DateTimeField(
        null=True,
        blank=True
    )


    # ======================================================
    # VALIDACIONES
    # ======================================================

    def clean(self):

        # ==================================================
        # HORARIO PERMITIDO
        # ==================================================

        if (
            self.time.hour < 13
            or self.time.hour >= 19
        ):

            raise ValidationError(
                "Las citas solo se permiten de 1PM a 7PM."
            )


        # ==================================================
        # EVITAR CITAS DUPLICADAS
        # ==================================================

        exists = Appointment.objects.filter(

            patient=self.patient,

            date=self.date,

            time=self.time

        ).exclude(

            id=self.id

        ).exists()


        if exists:

            raise ValidationError(
                "Ya existe una cita para este paciente "
                "en esta fecha y hora."
            )


    # ======================================================
    # GUARDAR
    # ======================================================

    def save(
        self,
        *args,
        **kwargs
    ):

        self.clean()

        super().save(
            *args,
            **kwargs
        )


    # ======================================================
    # REPRESENTACIÓN
    # ======================================================

    def __str__(self):

        patient_name = (

            self.patient.get_full_name()

            or

            self.patient.username

        )

        return (

            f"{patient_name} - "
            f"{self.date} "
            f"{self.time}"

        )

