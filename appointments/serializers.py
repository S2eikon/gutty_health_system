# ======================================================
# APPOINTMENTS / SERIALIZERS.PY
# VERSIÓN CORREGIDA (SIN VALIDACIÓN DE PROFESIONALES)
# ======================================================

from rest_framework import serializers

from users.models import User

from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):

    # ==================================================
    # INFORMACIÓN DEL PACIENTE
    # ==================================================

    patient_name = serializers.SerializerMethodField()

    # ==================================================
    # INFORMACIÓN DEL MÉDICO
    # ==================================================

    doctor_name = serializers.SerializerMethodField()

    # ==================================================
    # INFORMACIÓN DE LA ESTETICISTA
    # ==================================================

    esthetician_name = serializers.SerializerMethodField()

    # ==================================================
    # ESTADO
    # ==================================================

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    # ==================================================
    # TIPO DE CITA
    # ==================================================

    appointment_type_display = serializers.CharField(
        source="get_appointment_type_display",
        read_only=True,
    )

    # ==================================================
    # PACIENTE - PERMITIR CUALQUIER USUARIO
    # ==================================================

    patient = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=True,
        allow_null=False,
    )

    # ==================================================
    # CONFIGURACIÓN
    # ==================================================

    class Meta:

        model = Appointment

        fields = [
            "id",

            "patient",
            "patient_name",

            "doctor",
            "doctor_name",

            "esthetician",
            "esthetician_name",

            "appointment_type",
            "appointment_type_display",

            "date",
            "time",

            "status",
            "status_display",
        ]

        read_only_fields = [
            "id",

            "patient_name",
            "doctor_name",
            "esthetician_name",

            "status",
            "status_display",

            "appointment_type_display",
        ]

    # ======================================================
    # NOMBRE DEL PACIENTE
    # ======================================================

    def get_patient_name(
        self,
        obj: Appointment,
    ) -> str:

        if obj.patient:

            return (
                obj.patient.get_full_name()
                or
                obj.patient.username
            )

        return ""

    # ======================================================
    # NOMBRE DEL MÉDICO
    # ======================================================

    def get_doctor_name(
        self,
        obj: Appointment,
    ) -> str:

        if obj.doctor:

            return (
                obj.doctor.get_full_name()
                or
                obj.doctor.username
            )

        return ""

    # ======================================================
    # NOMBRE DE LA ESTETICISTA
    # ======================================================

    def get_esthetician_name(
        self,
        obj: Appointment,
    ) -> str:

        if obj.esthetician:

            return (
                obj.esthetician.get_full_name()
                or
                obj.esthetician.username
            )

        return ""

    # ======================================================
    # VALIDACIÓN - CORREGIDA
    # ======================================================

    def validate(
        self,
        data: dict,
    ) -> dict:

        print(
            "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
            "========================================"
        )

        print(
            "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
            "Iniciando validación de cita."
        )

        # ==================================================
        # USUARIO AUTENTICADO
        # ==================================================

        request = self.context.get("request")

        authenticated_user = None

        if (
            request is not None
            and request.user.is_authenticated
        ):

            authenticated_user = request.user

        if authenticated_user:

            print(
                "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
                f"Usuario autenticado: "
                f"{authenticated_user.username}"
            )

            print(
                "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
                f"Rol: {authenticated_user.role}"
            )

        # ==================================================
        # OPERACIÓN
        # ==================================================

        is_create = self.instance is None

        is_partial_update = (
            self.instance is not None
            and self.partial
        )

        is_full_update = (
            self.instance is not None
            and not self.partial
        )

        # ==================================================
        # VALIDAR PACIENTE
        # ==================================================

        patient = data.get("patient")

        if patient is None:

            raise serializers.ValidationError({
                "patient": "El paciente es obligatorio."
            })

        # ==================================================
        # TIPO DE CITA
        # ==================================================

        appointment_type = data.get(
            "appointment_type",
        )

        if is_create and not appointment_type:

            raise serializers.ValidationError({
                "appointment_type":
                "Este campo es obligatorio.",
            })

        if is_full_update and not appointment_type:

            raise serializers.ValidationError({
                "appointment_type":
                "Este campo es obligatorio.",
            })

        if (
            is_partial_update
            and appointment_type is None
        ):

            appointment_type = (
                self.instance.appointment_type
            )

            data["appointment_type"] = appointment_type

        # ==================================================
        # FECHA
        # ==================================================

        appointment_date = data.get("date")

        if is_create and not appointment_date:

            raise serializers.ValidationError({
                "date":
                "Este campo es obligatorio.",
            })

        if is_full_update and not appointment_date:

            raise serializers.ValidationError({
                "date":
                "Este campo es obligatorio.",
            })

        if (
            is_partial_update
            and appointment_date is None
        ):

            appointment_date = self.instance.date

            data["date"] = appointment_date

        # ==================================================
        # HORA
        # ==================================================

        appointment_time = data.get("time")

        if is_create and not appointment_time:

            raise serializers.ValidationError({
                "time":
                "Este campo es obligatorio.",
            })

        if is_full_update and not appointment_time:

            raise serializers.ValidationError({
                "time":
                "Este campo es obligatorio.",
            })

        if (
            is_partial_update
            and appointment_time is None
        ):

            appointment_time = self.instance.time

            data["time"] = appointment_time

        # ==================================================
        # PROFESIONALES
        # ==================================================

        if is_partial_update:

            if "doctor" not in data:

                doctor = self.instance.doctor

                data["doctor"] = doctor

            else:

                doctor = data.get("doctor")

            if "esthetician" not in data:

                esthetician = self.instance.esthetician

                data["esthetician"] = esthetician

            else:

                esthetician = data.get(
                    "esthetician",
                )

        else:

            doctor = data.get("doctor")

            esthetician = data.get(
                "esthetician",
            )

        # ==================================================
        # ⬇️⬇️⬇️ VALIDACIÓN ELIMINADA ⬇️⬇️⬇️
        # Ya no se valida que no puedan tener ambos profesionales
        # ==================================================

        # ==================================================
        # VALIDAR DOCTOR
        # ==================================================

        if doctor:

            if doctor.role != "doctor":

                raise serializers.ValidationError({
                    "doctor":
                    "El usuario seleccionado no tiene "
                    "el rol de doctor.",
                })

        # ==================================================
        # VALIDAR ESTETICISTA
        # ==================================================

        if esthetician:

            if esthetician.role != "esthetician":

                raise serializers.ValidationError({
                    "esthetician":
                    "El usuario seleccionado no tiene "
                    "el rol de esteticista.",
                })

        # ==================================================
        # VALIDAR TIPO DE CITA
        # ==================================================

        valid_types = dict(
            Appointment.TYPE_CHOICES
        )

        if appointment_type not in valid_types:

            raise serializers.ValidationError({
                "appointment_type":
                "El tipo de cita seleccionado no es válido.",
            })

        # ==================================================
        # VALIDACIÓN DE ESTADO
        # ==================================================

        if self.instance is not None:

            current_status = self.instance.status

            if current_status == "cancelled":

                raise serializers.ValidationError({
                    "status":
                    "Una cita cancelada no puede modificarse.",
                })

        # ==================================================
        # VALIDAR DISPONIBILIDAD DEL PACIENTE
        # ==================================================

        duplicate_appointment = Appointment.objects.filter(
            patient=patient,
            date=appointment_date,
            time=appointment_time,
        )

        if self.instance is not None:

            duplicate_appointment = (
                duplicate_appointment.exclude(
                    pk=self.instance.pk,
                )
            )

        if duplicate_appointment.exists():

            raise serializers.ValidationError({
                "date":
                "Ya existe una cita para este paciente "
                "en esta fecha y hora.",
            })

        # ==================================================
        # AUDITORÍA
        # ==================================================

        print(
            "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
            f"Paciente: {patient.username if patient else 'Sin asignar'}"
        )

        print(
            "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
            f"Fecha: {appointment_date}"
        )

        print(
            "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
            f"Hora: {appointment_time}"
        )

        print(
            "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
            f"Tipo: {appointment_type}"
        )

        print(
            "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
            f"Doctor: "
            f"{doctor.username if doctor else 'Sin asignar'}"
        )

        print(
            "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
            f"Esteticista: "
            f"{esthetician.username if esthetician else 'Sin asignar'}"
        )

        print(
            "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
            "Validación correcta."
        )

        print(
            "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
            "========================================"
        )

        return data