from rest_framework import serializers

from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):

    # ======================================================
    # INFORMACIÓN DEL PACIENTE
    # ======================================================

    patient_name = serializers.SerializerMethodField()

    # ======================================================
    # INFORMACIÓN DEL MÉDICO
    # ======================================================

    doctor_name = serializers.SerializerMethodField()

    # ======================================================
    # ESTADO DE LA CITA
    # ======================================================

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True
    )

    # ======================================================
    # TIPO DE CITA
    # ======================================================

    appointment_type_display = serializers.CharField(
        source="get_appointment_type_display",
        read_only=True
    )

    # ======================================================
    # CONFIGURACIÓN DEL SERIALIZER
    # ======================================================

    class Meta:

        model = Appointment

        fields = [

            "id",

            # ----------------------------------------------
            # PACIENTE
            # ----------------------------------------------

            "patient",
            "patient_name",

            # ----------------------------------------------
            # MÉDICO
            # ----------------------------------------------

            "doctor",
            "doctor_name",

            # ----------------------------------------------
            # TIPO DE CITA
            # ----------------------------------------------

            "appointment_type",
            "appointment_type_display",

            # ----------------------------------------------
            # FECHA Y HORA
            # ----------------------------------------------

            "date",
            "time",

            # ----------------------------------------------
            # ESTADO
            # ----------------------------------------------

            "status",
            "status_display",

        ]

        # ==================================================
        # CAMPOS DE SOLO LECTURA
        # ==================================================

        read_only_fields = [

            "patient",

            "patient_name",

            "doctor_name",

            "status_display",

            "appointment_type_display",

        ]

    # ======================================================
    # NOMBRE DEL PACIENTE
    # ======================================================

    def get_patient_name(
        self,
        obj
    ):

        if obj.patient:

            return (
                obj.patient.get_full_name()
                or obj.patient.username
            )

        return ""

    # ======================================================
    # NOMBRE DEL MÉDICO
    # ======================================================

    def get_doctor_name(
        self,
        obj
    ):

        if obj.doctor:

            return (
                obj.doctor.get_full_name()
                or obj.doctor.username
            )

        return ""

    # ======================================================
    # VALIDACIONES
    # ======================================================

    def validate(
        self,
        data
    ):

        # ==================================================
        # VALIDAR TIPO DE CITA
        # ==================================================

        if (
            not self.instance
            and
            not data.get("appointment_type")
        ):

            raise serializers.ValidationError({

                "appointment_type":
                "Este campo es obligatorio."

            })

        # ==================================================
        # VALIDAR FECHA
        # ==================================================

        if (
            not self.instance
            and
            not data.get("date")
        ):

            raise serializers.ValidationError({

                "date":
                "Este campo es obligatorio."

            })

        # ==================================================
        # VALIDAR HORA
        # ==================================================

        if (
            not self.instance
            and
            not data.get("time")
        ):

            raise serializers.ValidationError({

                "time":
                "Este campo es obligatorio."

            })

        return data