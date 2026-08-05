from rest_framework import serializers

from .models import Bill


# =====================================================
# SERIALIZER DE FACTURACIÓN
# =====================================================

class BillSerializer(serializers.ModelSerializer):

    # =================================================
    # NOMBRE DEL PACIENTE
    # =================================================

    patient_name = serializers.SerializerMethodField()

    # =================================================
    # CONFIGURACIÓN
    # =================================================

    class Meta:

        model = Bill

        fields = [
            'id',
            'patient',
            'patient_name',
            'concept',
            'amount',
            'status',
            'created_at',
        ]

        # =============================================
        # CAMPOS PROTEGIDOS
        # =============================================

        read_only_fields = [
            'id',
            'created_at',
            'patient_name',
        ]

    # =================================================
    # VALIDAR CONCEPTO
    # =================================================

    def validate_concept(self, value):

        value = value.strip()

        if not value:

            raise serializers.ValidationError(
                "El concepto de la factura no puede estar vacío."
            )

        return value

    # =================================================
    # VALIDAR VALOR
    # =================================================

    def validate_amount(self, value):

        if value <= 0:

            raise serializers.ValidationError(
                "El valor de la factura debe ser mayor que cero."
            )

        return value

    # =================================================
    # OBTENER NOMBRE DEL PACIENTE
    # =================================================

    def get_patient_name(self, obj):

        return (
            obj.patient.get_full_name()
            or obj.patient.username
        )

