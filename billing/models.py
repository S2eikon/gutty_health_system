from django.db import models
from users.models import User


# =====================================================
# MODELO DE FACTURACIÓN
# =====================================================

class Bill(models.Model):

    # =================================================
    # ESTADOS DE LA FACTURA
    # =================================================

    STATUS = [
        ('pending', 'Pendiente'),
        ('paid', 'Pagada'),
        ('cancelled', 'Cancelada'),
    ]

    # =================================================
    # PACIENTE
    # =================================================

    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bills',
        verbose_name='Paciente'
    )

    # =================================================
    # CONCEPTO DE LA FACTURA
    # =================================================

    concept = models.CharField(
        max_length=150,
        verbose_name='Concepto'
    )

    # =================================================
    # VALOR DE LA FACTURA
    # =================================================

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Valor'
    )

    # =================================================
    # ESTADO DE LA FACTURA
    # =================================================

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='pending',
        verbose_name='Estado'
    )

    # =================================================
    # FECHA DE CREACIÓN
    # =================================================

    created_at = models.DateField(
        auto_now_add=True,
        verbose_name='Fecha'
    )

    # =================================================
    # CONFIGURACIÓN DEL MODELO
    # =================================================

    class Meta:

        ordering = ['-created_at']

        verbose_name = 'Factura'

        verbose_name_plural = 'Facturas'

    # =================================================
    # REPRESENTACIÓN DEL OBJETO
    # =================================================

    def __str__(self):

        return (
            f'{self.patient.username} - '
            f'${self.amount}'
        )

