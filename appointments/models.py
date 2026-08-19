# ======================================================
# APPOINTMENTS / MODELS.PY
# GUTTY HEALTH SYSTEM
# ======================================================

from django.db import models
from django.core.exceptions import ValidationError

from users.models import User


# ======================================================
# MODELO DE CITAS
# ======================================================

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
    # ESTETICISTA
    # ======================================================

    esthetician = models.ForeignKey(

        User,

        on_delete=models.SET_NULL,

        null=True,

        blank=True,

        related_name='appointments_as_esthetician'

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
    # ======================================================
    #
    # Estos campos registran el envío de recordatorios
    # por correo electrónico.
    #
    # Son independientes de las notificaciones
    # internas del sistema.
    #
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
        # VALIDAR FECHA Y HORA
        # ==================================================

        if self.date is None:

            raise ValidationError({

                'date':
                'La fecha de la cita es obligatoria.'

            })


        if self.time is None:

            raise ValidationError({

                'time':
                'La hora de la cita es obligatoria.'

            })


        # ==================================================
        # VALIDAR PACIENTE
        # ==================================================

        if self.patient is None:

            raise ValidationError({

                'patient':
                'El paciente es obligatorio.'

            })


        # ==================================================
        # VALIDAR ROL DEL PACIENTE
        # ==================================================

        if self.patient.role != 'patient':

            raise ValidationError({

                'patient':
                'El usuario seleccionado debe tener '
                'el rol de paciente.'

            })


        # ==================================================
        # VALIDAR HORARIO
        # ==================================================
        #
        # Las citas están permitidas desde las 13:00
        # hasta las 19:00.
        #
        # 13:00 -> permitido
        # 18:59 -> permitido
        # 19:00 -> permitido
        #
        # Después de las 19:00 -> rechazado.
        #
        # ==================================================

        from datetime import time

        opening_time = time(

            hour=13,

            minute=0

        )

        closing_time = time(

            hour=19,

            minute=0

        )


        if not (

            opening_time
            <=
            self.time
            <=
            closing_time

        ):

            raise ValidationError({

                'time':
                'Las citas solo se permiten '
                'de 1:00 PM a 7:00 PM.'

            })


        # ==================================================
        # VALIDAR DOCTOR
        # ==================================================

        if self.doctor is not None:

            if self.doctor.role != 'doctor':

                raise ValidationError({

                    'doctor':
                    'El usuario seleccionado como doctor '
                    'debe tener el rol Doctor.'

                })


        # ==================================================
        # VALIDAR ESTETICISTA
        # ==================================================

        if self.esthetician is not None:

            if self.esthetician.role != 'esthetician':

                raise ValidationError({

                    'esthetician':
                    'El usuario seleccionado como esteticista '
                    'debe tener el rol Esteticista.'

                })


        # ==================================================
        # VALIDAR PROFESIONAL ASIGNADO
        # ==================================================
        #
        # Una cita no puede tener simultáneamente:
        #
        # - Doctor
        # - Esteticista
        #
        # Debe tener uno de los dos o ninguno,
        # dependiendo de las reglas del negocio.
        #
        # ==================================================

        if (

            self.doctor is not None

            and

            self.esthetician is not None

        ):

            raise ValidationError({

                'professional':
                'Una cita no puede tener un doctor y '
                'una esteticista asignados al mismo tiempo.'

            })


        # ==================================================
        # EVITAR CITAS DUPLICADAS
        # ==================================================
        #
        # Un mismo paciente no puede tener dos citas
        # exactamente en la misma fecha y hora.
        #
        # Se excluye la propia cita cuando se está editando.
        #
        # ==================================================

        exists = Appointment.objects.filter(

            patient=self.patient,

            date=self.date,

            time=self.time

        ).exclude(

            id=self.id

        ).exists()


        if exists:

            raise ValidationError({

                'date':
                'Ya existe una cita para este paciente '
                'en esta fecha y hora.'

            })


    # ======================================================
    # GUARDAR
    # ======================================================

    def save(

        self,

        *args,

        **kwargs

    ):

        # ==================================================
        # EJECUTAR VALIDACIONES ANTES DE GUARDAR
        # ==================================================

        self.clean()


        # ==================================================
        # GUARDAR EN BASE DE DATOS
        # ==================================================

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