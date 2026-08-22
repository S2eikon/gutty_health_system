# ======================================================
# APPOINTMENTS / VIEWS.PY
# GUTTY HEALTH SYSTEM
# AUDITORÍA Y SEGURIDAD COMPLETA
# ======================================================

from django.conf import settings
from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from users.permissions import (
    IsAdmin,
    IsAdminOrDoctor,
    IsAdminOrPatient,
    IsAdminOrReceptionist,
    IsAdminDoctorPatientReceptionist,
)

from .models import Appointment
from .serializers import AppointmentSerializer

from audit.services import create_audit


# ======================================================
# LISTAR CITAS
# ======================================================

@api_view(["GET"])
@permission_classes([IsAdminDoctorPatientReceptionist])
def appointments_api(request):

    print(
        "[AUDITORÍA][APPOINTMENTS] "
        "Consulta de listado de citas."
    )

    # ==================================================
    # FILTRAR SEGÚN ROL
    # ==================================================

    if request.user.role == "patient":

        appointments = Appointment.objects.filter(
            patient=request.user,
        ).select_related(
            "patient",
            "doctor",
            "esthetician",
        ).order_by(
            "date",
            "time",
        )

    else:

        appointments = Appointment.objects.select_related(
            "patient",
            "doctor",
            "esthetician",
        ).order_by(
            "date",
            "time",
        )

    # ==================================================
    # PAGINACIÓN
    # ==================================================

    paginator = PageNumberPagination()

    paginator.page_size = 20
    paginator.page_size_query_param = "page_size"
    paginator.max_page_size = 100

    paginated_appointments = paginator.paginate_queryset(
        appointments,
        request,
    )

    serializer = AppointmentSerializer(
        paginated_appointments,
        many=True,
        context={
            "request": request,
        },
    )

    # ==================================================
    # AUDITORÍA
    # ==================================================

    create_audit(
        user=request.user,
        action="read",
        module="appointments",
        object_id=None,
        description=(
            f"El usuario {request.user.username} "
            f"consultó la lista de citas."
        ),
        request=request,
    )

    return paginator.get_paginated_response(
        serializer.data,
    )


# ======================================================
# CREAR CITA - CON DOCTOR Y ESTETICISTA SIEMPRE
# ======================================================

@api_view(["POST"])
@permission_classes([IsAdminOrPatient])
def create_appointment_api(request):

    print(
        "[AUDITORÍA][APPOINTMENTS] "
        "Solicitud para crear cita."
    )

    # ==================================================
    # OBTENER EL TIPO DE CITA
    # ==================================================

    appointment_type = request.data.get("appointment_type")

    # ==================================================
    # DATOS BASE
    # ==================================================

    data = {
        "patient": request.user.id,
        "appointment_type": appointment_type,
        "date": request.data.get("date"),
        "time": request.data.get("time"),
    }

    # ==================================================
    # ASIGNAR AMBOS PROFESIONALES SIEMPRE
    # ==================================================

    # Siempre asignar doctor (Asdrúbal Gutty - ID: 2)
    data['doctor'] = 2

    # Siempre asignar esteticista (Luz Constanza - ID: 14)
    data['esthetician'] = 14

    print(
        "[AUDITORÍA][APPOINTMENTS] "
        f"Asignando doctor (ID:2) y esteticista (ID:14) a cita tipo: {appointment_type}"
    )

    print(
        "[AUDITORÍA][APPOINTMENTS] "
        f"Datos a crear: {data}"
    )

    serializer = AppointmentSerializer(
        data=data,
        context={
            "request": request,
        },
    )

    if not serializer.is_valid():

        print(
            "[AUDITORÍA][APPOINTMENTS] "
            f"Error de validación: {serializer.errors}"
        )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:

        with transaction.atomic():

            appointment = serializer.save()

            create_audit(
                user=request.user,
                action="create",
                module="appointments",
                object_id=appointment.id,
                description=(
                    f"El usuario {request.user.username} "
                    f"creó la cita con ID "
                    f"{appointment.id}."
                ),
                request=request,
            )

    except IntegrityError:

        print(
            "[AUDITORÍA][APPOINTMENTS] "
            "Conflicto de integridad al crear cita."
        )

        return Response(
            {
                "error":
                "No fue posible crear la cita porque "
                "ya existe una cita del mismo paciente "
                "en la misma fecha y hora.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    except Exception as exc:

        print(
            "[AUDITORÍA][APPOINTMENTS] "
            f"Error al crear cita: {exc}"
        )

        return Response(
            {
                "error":
                "No fue posible crear la cita. "
                "Verifique los datos ingresados.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        AppointmentSerializer(
            appointment,
            context={
                "request": request,
            },
        ).data,
        status=status.HTTP_201_CREATED,
    )


# ======================================================
# ACTUALIZAR CITA
# ======================================================

@api_view(["PUT"])
@permission_classes([IsAdminOrPatient])
def update_appointment_api(
    request,
    appointment_id,
):

    # ==================================================
    # OBTENER CITA SEGÚN ROL
    # ==================================================

    if request.user.role == "patient":

        appointment = get_object_or_404(
            Appointment,
            id=appointment_id,
            patient=request.user,
        )

    else:

        appointment = get_object_or_404(
            Appointment,
            id=appointment_id,
        )

    # ==================================================
    # VALIDAR ESTADO
    # ==================================================

    if appointment.status == "cancelled":

        return Response(
            {
                "error":
                "Una cita cancelada no puede modificarse.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ==================================================
    # DATOS ANTERIORES
    # ==================================================

    old_date = appointment.date
    old_time = appointment.time
    old_type = appointment.appointment_type
    old_doctor = appointment.doctor
    old_esthetician = appointment.esthetician

    # ==================================================
    # SERIALIZACIÓN
    # ==================================================

    serializer = AppointmentSerializer(
        appointment,
        data=request.data,
        partial=True,
        context={
            "request": request,
        },
    )

    if not serializer.is_valid():

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:

        with transaction.atomic():

            appointment = serializer.save()

            changes = []

            if old_date != appointment.date:

                changes.append(
                    f"fecha: {old_date} → "
                    f"{appointment.date}"
                )

            if old_time != appointment.time:

                changes.append(
                    f"hora: {old_time} → "
                    f"{appointment.time}"
                )

            if old_type != appointment.appointment_type:

                changes.append(
                    f"tipo: {old_type} → "
                    f"{appointment.appointment_type}"
                )

            if old_doctor != appointment.doctor:

                old_name = (
                    old_doctor.username
                    if old_doctor
                    else "Sin asignar"
                )

                new_name = (
                    appointment.doctor.username
                    if appointment.doctor
                    else "Sin asignar"
                )

                changes.append(
                    f"doctor: {old_name} → {new_name}"
                )

            if old_esthetician != appointment.esthetician:

                old_name = (
                    old_esthetician.username
                    if old_esthetician
                    else "Sin asignar"
                )

                new_name = (
                    appointment.esthetician.username
                    if appointment.esthetician
                    else "Sin asignar"
                )

                changes.append(
                    "esteticista: "
                    f"{old_name} → {new_name}"
                )

            description = (
                f"El usuario {request.user.username} "
                f"actualizó la cita con ID "
                f"{appointment.id}."
            )

            if changes:

                description += (
                    " Cambios: "
                    + "; ".join(changes)
                    + "."
                )

            create_audit(
                user=request.user,
                action="update",
                module="appointments",
                object_id=appointment.id,
                description=description,
                request=request,
            )

    except IntegrityError:

        return Response(
            {
                "error":
                "No fue posible actualizar la cita "
                "porque ya existe otra cita del paciente "
                "en la misma fecha y hora.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    except Exception as exc:

        print(
            "[AUDITORÍA][APPOINTMENTS] "
            f"Error al actualizar cita: {exc}"
        )

        return Response(
            {
                "error":
                "No fue posible actualizar la cita. "
                "Verifique los datos ingresados.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        AppointmentSerializer(
            appointment,
            context={
                "request": request,
            },
        ).data,
        status=status.HTTP_200_OK,
    )


# ======================================================
# CONFIRMAR CITA
# ======================================================

@api_view(["PATCH"])
@permission_classes([IsAdminOrDoctor])
def confirm_appointment_api(
    request,
    appointment_id,
):

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
    )

    if appointment.status == "confirmed":

        return Response(
            {
                "error":
                "La cita ya está confirmada.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if appointment.status == "cancelled":

        return Response(
            {
                "error":
                "No se puede confirmar una cita cancelada.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    old_status = appointment.status

    with transaction.atomic():

        appointment.status = "confirmed"

        appointment.save(
            update_fields=[
                "status",
            ],
        )

        create_audit(
            user=request.user,
            action="confirm",
            module="appointments",
            object_id=appointment.id,
            description=(
                f"El usuario {request.user.username} "
                f"cambió el estado de la cita "
                f"{appointment.id}: "
                f"{old_status} → confirmed."
            ),
            request=request,
        )

    return Response(
        {
            "message":
            "Cita confirmada correctamente.",
        },
        status=status.HTTP_200_OK,
    )


# ======================================================
# CANCELAR CITA
# ======================================================

@api_view(["PATCH"])
@permission_classes([IsAdminOrDoctor])
def cancel_appointment_api(
    request,
    appointment_id,
):

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
    )

    if appointment.status == "cancelled":

        return Response(
            {
                "error":
                "La cita ya fue cancelada.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    old_status = appointment.status

    with transaction.atomic():

        appointment.status = "cancelled"

        appointment.save(
            update_fields=[
                "status",
            ],
        )

        create_audit(
            user=request.user,
            action="cancel",
            module="appointments",
            object_id=appointment.id,
            description=(
                f"El usuario {request.user.username} "
                f"canceló la cita {appointment.id}. "
                f"Estado anterior: {old_status}."
            ),
            request=request,
        )

    return Response(
        {
            "message":
            "Cita cancelada correctamente.",
        },
        status=status.HTTP_200_OK,
    )


# ======================================================
# REPROGRAMAR CITA
# ======================================================

@api_view(["PATCH"])
@permission_classes([IsAdminOrReceptionist])
def reschedule_appointment_api(
    request,
    appointment_id,
):

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
    )

    # ==================================================
    # VALIDAR ESTADO
    # ==================================================

    if appointment.status == "cancelled":

        return Response(
            {
                "error":
                "No se puede reprogramar una cita cancelada.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ==================================================
    # VALIDAR QUE REALMENTE SE QUIERA REPROGRAMAR
    # ==================================================

    if (
        "date" not in request.data
        and "time" not in request.data
    ):

        return Response(
            {
                "error":
                "Para reprogramar debe proporcionar "
                "una nueva fecha, una nueva hora o ambas.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    old_date = appointment.date
    old_time = appointment.time
    old_status = appointment.status

    # ==================================================
    # VALIDAR DATOS
    # ==================================================

    serializer = AppointmentSerializer(
        appointment,
        data=request.data,
        partial=True,
        context={
            "request": request,
        },
    )

    if not serializer.is_valid():

        print(
            "[AUDITORÍA][APPOINTMENTS] "
            f"Error al validar reprogramación: "
            f"{serializer.errors}"
        )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    new_date = serializer.validated_data.get(
        "date",
        appointment.date,
    )

    new_time = serializer.validated_data.get(
        "time",
        appointment.time,
    )

    # ==================================================
    # VALIDAR QUE EXISTA UN CAMBIO REAL
    # ==================================================

    if (
        new_date == old_date
        and new_time == old_time
    ):

        return Response(
            {
                "error":
                "La nueva fecha u hora debe ser "
                "diferente a la actual.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:

        with transaction.atomic():

            appointment = serializer.save()

            appointment.status = "rescheduled"

            appointment.save(
                update_fields=[
                    "status",
                ],
            )

            create_audit(
                user=request.user,
                action="reschedule",
                module="appointments",
                object_id=appointment.id,
                description=(
                    f"El usuario {request.user.username} "
                    f"reprogramó la cita "
                    f"{appointment.id}. "
                    f"Fecha: {old_date} → "
                    f"{appointment.date}. "
                    f"Hora: {old_time} → "
                    f"{appointment.time}. "
                    f"Estado anterior: {old_status}."
                ),
                request=request,
            )

    except IntegrityError:

        print(
            "[AUDITORÍA][APPOINTMENTS] "
            "Conflicto de integridad al reprogramar cita."
        )

        return Response(
            {
                "error":
                "No fue posible reprogramar la cita "
                "porque ya existe otra cita del paciente "
                "en la nueva fecha y hora.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    except Exception as exc:

        print(
            "[AUDITORÍA][APPOINTMENTS] "
            f"Error al reprogramar cita: {exc}"
        )

        return Response(
            {
                "error":
                "No fue posible reprogramar la cita. "
                "Verifique que la nueva fecha y hora "
                "estén disponibles.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {
            "message":
            "Cita reprogramada correctamente.",

            "appointment":
            AppointmentSerializer(
                appointment,
                context={
                    "request": request,
                },
            ).data,
        },
        status=status.HTTP_200_OK,
    )


# ======================================================
# ELIMINAR CITA
# ======================================================

@api_view(["DELETE"])
@permission_classes([IsAdmin])
def delete_appointment_api(
    request,
    appointment_id,
):

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
    )

    appointment_id_deleted = appointment.id

    create_audit(
        user=request.user,
        action="delete",
        module="appointments",
        object_id=appointment_id_deleted,
        description=(
            f"El usuario {request.user.username} "
            f"eliminó la cita con ID "
            f"{appointment_id_deleted}."
        ),
        request=request,
    )

    appointment.delete()

    return Response(
        {
            "message":
            "Cita eliminada correctamente.",
        },
        status=status.HTTP_200_OK,
    )


# ======================================================
# DASHBOARD
# ======================================================

@api_view(["GET"])
@permission_classes([IsAdminDoctorPatientReceptionist])
def dashboard_totals_api(request):

    if request.user.role == "patient":

        appointments = Appointment.objects.filter(
            patient=request.user,
        )

    else:

        appointments = Appointment.objects.all()

    data = {
        "total":
        appointments.count(),

        "pending":
        appointments.filter(
            status="pending",
        ).count(),

        "confirmed":
        appointments.filter(
            status="confirmed",
        ).count(),

        "cancelled":
        appointments.filter(
            status="cancelled",
        ).count(),

        "rescheduled":
        appointments.filter(
            status="rescheduled",
        ).count(),
    }

    create_audit(
        user=request.user,
        action="read",
        module="appointments",
        object_id=None,
        description=(
            f"El usuario {request.user.username} "
            f"consultó el resumen del dashboard "
            f"de citas."
        ),
        request=request,
    )

    return Response(
        data,
        status=status.HTTP_200_OK,
    )


# ======================================================
# CALENDARIO
# ======================================================

@api_view(["GET"])
@permission_classes([IsAdminDoctorPatientReceptionist])
def calendar_appointments_api(request):

    if request.user.role == "patient":

        appointments = Appointment.objects.filter(
            patient=request.user,
        ).select_related(
            "patient",
            "doctor",
            "esthetician",
        ).order_by(
            "date",
            "time",
        )

    else:

        appointments = Appointment.objects.select_related(
            "patient",
            "doctor",
            "esthetician",
        ).order_by(
            "date",
            "time",
        )

    STATUS_COLORS = {
        "pending": "#ffc107",
        "confirmed": "#198754",
        "cancelled": "#dc3545",
        "rescheduled": "#0dcaf0",
    }

    events = []

    for appointment in appointments:

        patient_name = (
            appointment.patient.get_full_name()
            or appointment.patient.username
        )

        doctor_name = "Sin asignar"

        if appointment.doctor:

            doctor_name = (
                appointment.doctor.get_full_name()
                or appointment.doctor.username
            )

        esthetician_name = "Sin asignar"

        if appointment.esthetician:

            esthetician_name = (
                appointment.esthetician.get_full_name()
                or appointment.esthetician.username
            )

        events.append(
            {
                "id":
                appointment.id,

                "title":
                f"{patient_name} - "
                f"{appointment.get_appointment_type_display()}",

                "start":
                f"{appointment.date}T{appointment.time}",

                "color":
                STATUS_COLORS.get(
                    appointment.status,
                    "#6c757d",
                ),

                "extendedProps": {

                    "patient":
                    patient_name,

                    "doctor":
                    doctor_name,

                    "esthetician":
                    esthetician_name,

                    "status":
                    appointment.status,

                    "status_display":
                    appointment.get_status_display(),

                    "appointment_type":
                    appointment.get_appointment_type_display(),

                    "date":
                    str(appointment.date),

                    "time":
                    str(appointment.time)[:5],

                    "notes":
                    getattr(
                        appointment,
                        "notes",
                        "",
                    ),

                    "phone":
                    getattr(
                        appointment.patient,
                        "phone",
                        "",
                    ),

                    "email":
                    appointment.patient.email,
                },
            }
        )

    create_audit(
        user=request.user,
        action="read",
        module="appointments",
        object_id=None,
        description=(
            f"El usuario {request.user.username} "
            f"consultó el calendario de citas."
        ),
        request=request,
    )

    return Response(
        events,
        status=status.HTTP_200_OK,
    )


# ======================================================
# RECORDATORIOS PENDIENTES
# ======================================================

@api_view(["POST"])
@permission_classes([IsAdminDoctorPatientReceptionist])
def send_pending_reminders_api(request):

    # ==================================================
    # FILTRAR SEGÚN ROL
    # ==================================================

    if request.user.role == "patient":

        appointments = Appointment.objects.filter(
            patient=request.user,
            status="pending",
            reminder_sent=False,
        ).select_related(
            "patient",
            "doctor",
        )

    else:

        appointments = Appointment.objects.filter(
            status="pending",
            reminder_sent=False,
        ).select_related(
            "patient",
            "doctor",
        )

    enviados = 0

    for appointment in appointments:

        if not appointment.patient.email:

            continue

        doctor_name = "Sin asignar"

        if appointment.doctor:

            doctor_name = (
                appointment.doctor.get_full_name()
                or appointment.doctor.username
            )

        message = f"""
Hola {appointment.patient.get_full_name() or appointment.patient.username},

Este es un recordatorio de su cita médica.

Fecha: {appointment.date}
Hora: {appointment.time.strftime("%H:%M")}
Doctor: {doctor_name}
Tipo de cita: {appointment.get_appointment_type_display()}

Instituto Médico Asdrúbal Gutty
"""

        try:

            send_mail(
                "Recordatorio de cita médica",
                message,
                settings.DEFAULT_FROM_EMAIL,
                [appointment.patient.email],
                fail_silently=False,
            )

        except Exception as exc:

            print(
                "[AUDITORÍA][APPOINTMENTS] "
                f"Error enviando recordatorio de cita "
                f"{appointment.id}: {exc}"
            )

            continue

        appointment.reminder_sent = True
        appointment.reminder_sent_at = timezone.now()

        appointment.save(
            update_fields=[
                "reminder_sent",
                "reminder_sent_at",
            ],
        )

        enviados += 1

    # ==================================================
    # AUDITORÍA
    # ==================================================

    if enviados > 0:

        create_audit(
            user=request.user,
            action="response",
            module="appointments",
            object_id=None,
            description=(
                f"El usuario {request.user.username} "
                f"envió {enviados} recordatorio(s) "
                f"de citas médicas."
            ),
            request=request,
        )

    return Response(
        {
            "message":
            f"Se enviaron {enviados} recordatorios.",
        },
        status=status.HTTP_200_OK,
    )


# ======================================================
# RECORDATORIO INDIVIDUAL
# ======================================================

@api_view(["POST"])
@permission_classes([IsAdminDoctorPatientReceptionist])
def send_reminder_api(
    request,
    appointment_id,
):

    # ==================================================
    # OBTENER CITA
    # ==================================================

    if request.user.role == "patient":

        appointment = get_object_or_404(
            Appointment,
            id=appointment_id,
            patient=request.user,
        )

    else:

        appointment = get_object_or_404(
            Appointment,
            id=appointment_id,
        )

    # ==================================================
    # VALIDAR ESTADO
    # ==================================================

    if appointment.status == "cancelled":

        return Response(
            {
                "error":
                "No se puede enviar un recordatorio "
                "de una cita cancelada.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ==================================================
    # VALIDAR CORREO
    # ==================================================

    if not appointment.patient.email:

        return Response(
            {
                "error":
                "El paciente no tiene un correo registrado.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    subject = "Recordatorio de cita médica"

    doctor_name = "Sin asignar"

    if appointment.doctor:

        doctor_name = (
            appointment.doctor.get_full_name()
            or appointment.doctor.username
        )

    message = f"""
Hola {appointment.patient.get_full_name() or appointment.patient.username},

Este es un recordatorio de su cita médica.

Fecha: {appointment.date}
Hora: {appointment.time.strftime("%H:%M")}
Doctor: {doctor_name}
Tipo de cita: {appointment.get_appointment_type_display()}

Por favor llegue con 15 minutos de anticipación.

Instituto Médico Asdrúbal Gutty
"""

    try:

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [appointment.patient.email],
            fail_silently=False,
        )

    except Exception as exc:

        print(
            "[AUDITORÍA][APPOINTMENTS] "
            f"Error enviando recordatorio de cita "
            f"{appointment.id}: {exc}"
        )

        return Response(
            {
                "error":
                "No fue posible enviar el recordatorio. "
                "Verifique la configuración del correo.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    appointment.reminder_sent = True
    appointment.reminder_sent_at = timezone.now()

    appointment.save(
        update_fields=[
            "reminder_sent",
            "reminder_sent_at",
        ],
    )

    # ==================================================
    # AUDITORÍA
    # ==================================================

    create_audit(
        user=request.user,
        action="response",
        module="appointments",
        object_id=appointment.id,
        description=(
            f"El usuario {request.user.username} "
            f"envió un recordatorio para la cita "
            f"{appointment.id}."
        ),
        request=request,
    )

    return Response(
        {
            "message":
            "Recordatorio enviado correctamente.",
        },
        status=status.HTTP_200_OK,
    )