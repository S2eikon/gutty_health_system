from django.db import models
from users.models import User

class Bill(models.Model):

    STATUS = [
        ('pending', 'Pendiente'),
        ('paid', 'Pagada'),
        ('cancelled', 'Cancelada'),
    ]

    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bills',
        verbose_name='Paciente'
    )

    concept = models.CharField(
        max_length=150,
        verbose_name='Concepto'
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Valor'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='pending',
        verbose_name='Estado'
    )

    created_at = models.DateField(
        auto_now_add=True,
        verbose_name='Fecha'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Factura'
        verbose_name_plural = 'Facturas'

    def __str__(self):
        return f'{self.patient.username} - ${self.amount}'
