from django.db import models
from django.conf import settings


class AuditLog(models.Model):

    # ==========================================
    # ACCIONES
    # ==========================================

    ACTION_CHOICES = [

        ("create", "Crear"),

        ("update", "Actualizar"),

        ("delete", "Eliminar"),

        ("confirm", "Confirmar"),

        ("cancel", "Cancelar"),

        ("login", "Inicio de sesión"),

        ("logout", "Cerrar sesión"),

        ("upload", "Subir archivo"),

        ("download", "Descargar archivo"),

        ("response", "Responder"),

    ]

    # ==========================================
    # USUARIO
    # ==========================================

    user = models.ForeignKey(

        settings.AUTH_USER_MODEL,

        on_delete=models.CASCADE,

        related_name="audit_logs"

    )

    # ==========================================
    # ACCIÓN REALIZADA
    # ==========================================

    action = models.CharField(

        max_length=20,

        choices=ACTION_CHOICES

    )

    # ==========================================
    # MÓDULO
    # ==========================================

    module = models.CharField(

        max_length=100

    )

    # ==========================================
    # ID DEL REGISTRO
    # ==========================================

    object_id = models.PositiveIntegerField(

        null=True,

        blank=True

    )

    # ==========================================
    # DESCRIPCIÓN
    # ==========================================

    description = models.TextField()

    # ==========================================
    # DIRECCIÓN IP
    # ==========================================

    ip_address = models.GenericIPAddressField(

        null=True,

        blank=True

    )

    # ==========================================
    # FECHA
    # ==========================================

    created_at = models.DateTimeField(

        auto_now_add=True

    )

    # ==========================================
    # REPRESENTACIÓN
    # ==========================================

    def __str__(self):

        return (

            f"{self.user.username} - "

            f"{self.action} - "

            f"{self.module}"

        )

    class Meta:

        ordering = ["-created_at"]

        verbose_name = "Registro de Auditoría"

        verbose_name_plural = "Registros de Auditoría"