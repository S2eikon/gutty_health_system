from django.db import models
from django.conf import settings


class Notification(models.Model):

    # ======================================================
    # TIPOS DE NOTIFICACIÓN
    # ======================================================

    TYPE_CHOICES = [

        (
            "new_appointment",
            "Nueva cita"
        ),

        (
            "appointment_confirmed",
            "Cita confirmada"
        ),

        (
            "appointment_cancelled",
            "Cita cancelada"
        ),

        (
            "appointment_rescheduled",
            "Cita reprogramada"
        ),

    ]


    # ======================================================
    # USUARIO QUE RECIBE LA NOTIFICACIÓN
    # ======================================================

    user = models.ForeignKey(

        settings.AUTH_USER_MODEL,

        on_delete=models.CASCADE,

        related_name="notifications"

    )


    # ======================================================
    # TIPO
    # ======================================================

    notification_type = models.CharField(

        max_length=50,

        choices=TYPE_CHOICES

    )


    # ======================================================
    # TÍTULO
    # ======================================================

    title = models.CharField(

        max_length=150

    )


    # ======================================================
    # MENSAJE
    # ======================================================

    message = models.TextField()


    # ======================================================
    # CITA RELACIONADA
    # ======================================================

    appointment_id = models.PositiveIntegerField(

        null=True,

        blank=True

    )


    # ======================================================
    # ESTADO DE LECTURA
    # ======================================================

    is_read = models.BooleanField(

        default=False

    )


    # ======================================================
    # FECHA DE CREACIÓN
    # ======================================================

    created_at = models.DateTimeField(

        auto_now_add=True

    )


    # ======================================================
    # ORDENAMIENTO
    # ======================================================

    class Meta:

        ordering = [
            "-created_at"
        ]


    # ======================================================
    # REPRESENTACIÓN
    # ======================================================

    def __str__(self):

        return (

            f"{self.title} - "

            f"{self.user.username}"

        )

