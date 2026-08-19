# ======================================================
# APPOINTMENTS / SERIALIZERS.PY
# GUTTY HEALTH SYSTEM
# AUDITORÍA Y VALIDACIÓN COMPLETA
# ======================================================

from rest_framework import serializers

from users.models import User

from .models import Appointment


# ======================================================
# SERIALIZADOR DE CITAS
# ======================================================

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
    # ESTADO DE LA CITA
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
    # PACIENTE
    # ==================================================

    patient = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(
            role="patient",
        ),
        required=False,
        allow_null=False,
    )

    # ==================================================
    # CONFIGURACIÓN
    # ==================================================

    class Meta:

        model = Appointment

        fields = [

            # ------------------------------------------
            # IDENTIFICACIÓN
            # ------------------------------------------

            "id",

            # ------------------------------------------
            # PACIENTE
            # ------------------------------------------

            "patient",
            "patient_name",

            # ------------------------------------------
            # MÉDICO
            # ------------------------------------------

            "doctor",
            "doctor_name",

            # ------------------------------------------
            # ESTETICISTA
            # ------------------------------------------

            "esthetician",
            "esthetician_name",

            # ------------------------------------------
            # TIPO DE CITA
            # ------------------------------------------

            "appointment_type",
            "appointment_type_display",

            # ------------------------------------------
            # FECHA Y HORA
            # ------------------------------------------

            "date",
            "time",

            # ------------------------------------------
            # ESTADO
            # ------------------------------------------

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
                or obj.patient.username
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
                or obj.doctor.username
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
                or obj.esthetician.username
            )

        return ""

    # ======================================================
    # VALIDACIÓN GENERAL
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
        # CONTEXTO DEL USUARIO AUTENTICADO
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

        else:

            print(
                "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
                "No se recibió usuario autenticado "
                "en el contexto del serializer."
            )

        # ==================================================
        # DETERMINAR OPERACIÓN
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

        print(
            "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
            "Operación: "
            f"{'CREACIÓN' if is_create else 'ACTUALIZACIÓN'}"
        )

        if is_partial_update:

            print(
                "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
                "Actualización parcial detectada."
            )

        if is_full_update:

            print(
                "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
                "Actualización completa detectada."
            )

        # ==================================================
        # PACIENTE
        # ==================================================

        patient = data.get("patient")

        # --------------------------------------------------
        # CREACIÓN COMO PACIENTE AUTENTICADO
        # --------------------------------------------------

        if (
            patient is None
            and is_create
            and authenticated_user is not None
            and authenticated_user.role == "patient"
        ):

            patient = authenticated_user

            print(
                "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
                "Paciente no enviado por frontend."
            )

            print(
                "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
                "Se utilizará automáticamente el usuario "
                f"autenticado: {patient.username}"
            )

        # --------------------------------------------------
        # ACTUALIZACIÓN SIN CAMBIAR PACIENTE
        # --------------------------------------------------

        elif (
            patient is None
            and self.instance is not None
        ):

            patient = self.instance.patient

            print(
                "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
                "No se recibió un nuevo paciente."
            )

            print(
                "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
                "Se conservará el paciente actual: "
                f"{patient.username if patient else 'Sin asignar'}"
            )

        # ==================================================
        # VALIDAR EXISTENCIA DEL PACIENTE
        # ==================================================

        if patient is None:

            print(
                "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
                "ERROR: Paciente no proporcionado."
            )

            raise serializers.ValidationError({
                "patient": (
                    "El paciente es obligatorio. "
                    "Seleccione un paciente antes de crear "
                    "la cita."
                ),
            })

        # ==================================================
        # VALIDAR ROL DEL PACIENTE
        # ==================================================

        if patient.role != "patient":

            print(
                "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
                "ERROR: El usuario seleccionado no tiene "
                "rol de paciente."
            )

            raise serializers.ValidationError({
                "patient": (
                    "El usuario seleccionado no tiene "
                    "el rol de paciente."
                ),
            })

        # ==================================================
        # SEGURIDAD PARA PACIENTES
        # ==================================================

        if (
            authenticated_user is not None
            and authenticated_user.role == "patient"
            and patient.id != authenticated_user.id
        ):

            print(
                "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
                "ERROR DE SEGURIDAD: El paciente "
                f"{authenticated_user.username} "
                "intentó utilizar otro paciente."
            )

            raise serializers.ValidationError({
                "patient": (
                    "No puede crear o modificar una cita "
                    "perteneciente a otro paciente."
                ),
            })

        # ==================================================
        # ASEGURAR PACIENTE EN DATA
        # ==================================================

        data["patient"] = patient

        print(
            "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
            f"Paciente validado: {patient.username}"
        )

        # ==================================================
        # TIPO DE CITA
        # ==================================================

        appointment_type = data.get(
            "appointment_type",
        )

        # --------------------------------------------------
        # CREACIÓN
        # --------------------------------------------------

        if is_create and not appointment_type:

            print(
                "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
                "ERROR: Tipo de cita no proporcionado."
            )

            raise serializers.ValidationError({
                "appointment_type": (
                    "Este campo es obligatorio."
                ),
            })

        # --------------------------------------------------
        # ACTUALIZACIÓN COMPLETA
        # --------------------------------------------------

        if (
            is_full_update
            and not appointment_type
        ):

            print(
                "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
                "ERROR: Tipo de cita no proporcionado "
                "durante actualización completa."
            )

            raise serializers.ValidationError({
                "appointment_type": (
                    "Este campo es obligatorio."
                ),
            })

        # --------------------------------------------------
        # ACTUALIZACIÓN PARCIAL
        # --------------------------------------------------

        if (
            is_partial_update
            and appointment_type is None
        ):

            appointment_type = (
                self.instance.appointment_type
            )

            data["appointment_type"] = appointment_type

            print(
                "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
                "Se conserva el tipo de cita actual: "
                f"{appointment_type}"
            )

        # ==================================================
        # FECHA
        # ==================================================

        appointment_date = data.get("date")

        # --------------------------------------------------
        # CREACIÓN
        # --------------------------------------------------

        if is_create and not appointment_date:

            print(
                "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
                "ERROR: Fecha no proporcionada."
            )

            raise serializers.ValidationError({
                "date": (
                    "Este campo es obligatorio."
                ),
            })

        # --------------------------------------------------
        # ACTUALIZACIÓN COMPLETA
        # --------------------------------------------------

        if (
            is_full_update
            and not appointment_date
        ):

            print(
                "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
                "ERROR: Fecha no proporcionada "
                "durante actualización completa."
            )

            raise serializers.ValidationError({
                "date": (
                    "Este campo es obligatorio."
                ),
            })

        # --------------------------------------------------
        # ACTUALIZACIÓN PARCIAL
        # --------------------------------------------------

        if (
            is_partial_update
            and appointment_date is None
        ):

            appointment_date = self.instance.date

            data["date"] = appointment_date

            print(
                "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
                "Se conserva la fecha actual: "
                f"{appointment_date}"
            )

        # ==================================================
        # HORA
        # ==================================================

        appointment_time = data.get("time")

        # --------------------------------------------------
        # CREACIÓN
        # --------------------------------------------------

        if is_create and not appointment_time:

            print(
                "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
                "ERROR: Hora no proporcionada."
            )

            raise serializers.ValidationError({
                "time": (
                    "Este campo es obligatorio."
                ),
            })

        # --------------------------------------------------
        # ACTUALIZACIÓN COMPLETA
        # --------------------------------------------------

        if (
            is_full_update
            and not appointment_time
        ):

            print(
                "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
                "ERROR: Hora no proporcionada "
                "durante actualización completa."
            )

            raise serializers.ValidationError({
                "time": (
                    "Este campo es obligatorio."
                ),
            })

        # --------------------------------------------------
        # ACTUALIZACIÓN PARCIAL
        # --------------------------------------------------

        if (
            is_partial_update
            and appointment_time is None
        ):

            appointment_time = self.instance.time

            data["time"] = appointment_time

            print(
                "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
                "Se conserva la hora actual: "
                f"{appointment_time}"
            )

        # ==================================================
        # PROFESIONALES
        # ==================================================

        if is_partial_update:

            # ----------------------------------------------
            # MÉDICO
            # ----------------------------------------------

            if "doctor" not in data:

                doctor = self.instance.doctor

                data["doctor"] = doctor

                print(
                    "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
                    "Se conserva el médico actual: "
                    f"{doctor.username if doctor else 'Sin asignar'}"
                )

            else:

                doctor = data.get("doctor")

            # ----------------------------------------------
            # ESTETICISTA
            # ----------------------------------------------

            if "esthetician" not in data:

                esthetician = (
                    self.instance.esthetician
                )

                data["esthetician"] = esthetician

                print(
                    "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
                    "Se conserva la esteticista actual: "
                    f"{esthetician.username if esthetician else 'Sin asignar'}"
                )

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
        # NO PERMITIR DOS PROFESIONALES
        # ==================================================

        if doctor and esthetician:

            print(
                "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
                "ERROR: Se intentaron asignar "
                "dos profesionales."
            )

            raise serializers.ValidationError({
                "professional": (
                    "Una cita no puede tener un doctor y "
                    "una esteticista asignados al mismo tiempo."
                ),
            })

        # ==================================================
        # VALIDAR DOCTOR
        # ==================================================

        if doctor:

            if doctor.role != "doctor":

                print(
                    "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
                    "ERROR: El usuario seleccionado como "
                    "doctor no tiene rol de doctor."
                )

                raise serializers.ValidationError({
                    "doctor": (
                        "El usuario seleccionado no tiene "
                        "el rol de doctor."
                    ),
                })

            print(
                "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
                f"Doctor validado: {doctor.username}"
            )

        # ==================================================
        # VALIDAR ESTETICISTA
        # ==================================================

        if esthetician:

            if esthetician.role != "esthetician":

                print(
                    "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
                    "ERROR: El usuario seleccionado como "
                    "esteticista no tiene rol válido."
                )

                raise serializers.ValidationError({
                    "esthetician": (
                        "El usuario seleccionado no tiene "
                        "el rol de esteticista."
                    ),
                })

            print(
                "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
                "Esteticista validada: "
                f"{esthetician.username}"
            )

        # ==================================================
        # AUDITORÍA DE DATOS
        # ==================================================

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
            f"Tipo de cita: {appointment_type}"
        )

        print(
            "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
            f"Médico: "
            f"{doctor.username if doctor else 'Sin asignar'}"
        )

        print(
            "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
            f"Esteticista: "
            f"{esthetician.username if esthetician else 'Sin asignar'}"
        )

        # ==================================================
        # AUDITORÍA FINAL
        # ==================================================

        print(
            "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
            "Validación correcta."
        )

        print(
            "[AUDITORÍA][SERIALIZER][APPOINTMENTS] "
            "========================================"
        )

        return data