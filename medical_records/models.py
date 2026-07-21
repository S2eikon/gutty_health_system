from django.db import models
from users.models import User


class MedicalRecord(models.Model):

    CONSULTA = [
        ('first', 'Primera consulta'),
        ('control', 'Control'),
        ('emergency', 'Urgencia'),
    ]

    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='medical_records',
        verbose_name='Paciente'
    )

    consultation = models.CharField(
        max_length=20,
        choices=CONSULTA,
        default='first',
        verbose_name='Consulta'
    )

    diagnosis = models.TextField(
        verbose_name='Diagnóstico'
    )

    medications = models.TextField(
        verbose_name='Medicamentos',
        default=''
    )

    observations = models.TextField(
        blank=True,
        default='',
        verbose_name='Observaciones'
    )

    created_at = models.DateField(
        auto_now_add=True,
        verbose_name='Fecha'
    )

    class Meta:
        verbose_name = 'Historial Médico'
        verbose_name_plural = 'Historiales Médicos'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.patient.username} - {self.get_consultation_display()} ({self.created_at})'