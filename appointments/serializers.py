from rest_framework import serializers
from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):

    patient_name = serializers.SerializerMethodField()

    doctor_name = serializers.SerializerMethodField()

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True
    )

    appointment_type_display = serializers.CharField(
        source="get_appointment_type_display",
        read_only=True
    )

    class Meta:
        model = Appointment

        fields = [
            "id",

            "patient",
            "patient_name",

            "doctor",
            "doctor_name",

            "appointment_type",
            "appointment_type_display",

            "date",
            "time",

            "status",
            "status_display",
        ]

        read_only_fields = [
            "patient",
            "patient_name",
            "doctor_name",
            "status_display",
            "appointment_type_display",
        ]

    # ==========================================
    # NOMBRE DEL PACIENTE
    # ==========================================

    def get_patient_name(self, obj):

        if obj.patient:

            return (
                obj.patient.get_full_name()
                or obj.patient.username
            )

        return ""

    # ==========================================
    # NOMBRE DEL MÉDICO
    # ==========================================

    def get_doctor_name(self, obj):

        if obj.doctor:

            return (
                obj.doctor.get_full_name()
                or obj.doctor.username
            )

        return ""

    # ==========================================
    # VALIDACIONES
    # ==========================================

    def validate(self, data):

        if not data.get("appointment_type"):

            raise serializers.ValidationError({
                "appointment_type": "Este campo es obligatorio."
            })

        if not data.get("date"):

            raise serializers.ValidationError({
                "date": "Este campo es obligatorio."
            })

        if not data.get("time"):

            raise serializers.ValidationError({
                "time": "Este campo es obligatorio."
            })

        return data