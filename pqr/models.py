from django.db import models
from django.conf import settings


class PQR(models.Model):

    # ==========================================
    # TIPO DE PQR
    # ==========================================

    TYPE_CHOICES = [

        ("petition", "Petición"),

        ("complaint", "Queja"),

        ("claim", "Reclamo"),

        ("suggestion", "Sugerencia"),

        ("praise", "Felicitación"),

    ]

    # ==========================================
    # ESTADOS
    # ==========================================

    STATUS_CHOICES = [

        ("open", "Abierta"),

        ("in_progress", "En proceso"),

        ("closed", "Cerrada"),

    ]

    # ==========================================
    # PACIENTE
    # ==========================================

    user = models.ForeignKey(

        settings.AUTH_USER_MODEL,

        on_delete=models.CASCADE,

        related_name="pqrs"

    )

    # ==========================================
    # INFORMACIÓN
    # ==========================================

    pqr_type = models.CharField(

        max_length=20,

        choices=TYPE_CHOICES

    )

    subject = models.CharField(

        max_length=200,

        blank=True,

        default=""

    )

    message = models.TextField()

    # ==========================================
    # RESPUESTA DEL ADMINISTRADOR
    # ==========================================

    response = models.TextField(

        blank=True,

        default=""

    )

    responded_by = models.ForeignKey(

        settings.AUTH_USER_MODEL,

        null=True,

        blank=True,

        on_delete=models.SET_NULL,

        related_name="answered_pqrs"

    )

    # ==========================================
    # ESTADO
    # ==========================================

    status = models.CharField(

        max_length=20,

        choices=STATUS_CHOICES,

        default="open"

    )

    # ==========================================
    # FECHAS
    # ==========================================

    created_at = models.DateTimeField(

        auto_now_add=True

    )

    updated_at = models.DateTimeField(

        auto_now=True

    )

    responded_at = models.DateTimeField(

        null=True,

        blank=True

    )

    # ==========================================
    # REPRESENTACIÓN
    # ==========================================

    def __str__(self):

        if self.subject:

            return f"{self.subject} - {self.user.username}"

        return f"{self.get_pqr_type_display()} - {self.user.username}"

    class Meta:

        ordering = ["-created_at"]

        verbose_name = "PQR"

        verbose_name_plural = "PQRs"