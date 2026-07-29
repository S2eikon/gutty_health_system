from django.db import models
from django.conf import settings


class MedicalDocument(models.Model):

    DOCUMENT_TYPES = [
        ("exam", "Examen"),
        ("photo", "Fotografía"),
        ("image", "Imagen"),
        ("prescription", "Fórmula médica"),
        ("consent", "Consentimiento informado"),
        ("order", "Orden médica"),
        ("other", "Otro"),
    ]


    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="documents"
    )


    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_documents"
    )


    title = models.CharField(
        max_length=200
    )


    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPES,
        default="other"
    )


    file = models.FileField(
        upload_to="medical_documents/%Y/%m/"
    )


    description = models.TextField(
        blank=True,
        null=True
    )


    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )


    class Meta:

        ordering = [
            "-uploaded_at"
        ]

        verbose_name = "Documento médico"

        verbose_name_plural = "Documentos médicos"


    def __str__(self):

        return f"{self.title} - {self.patient}"