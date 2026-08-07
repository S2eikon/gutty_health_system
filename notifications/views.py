from rest_framework.decorators import (
    api_view,
    permission_classes
)

from rest_framework.response import Response

from rest_framework import status

from django.shortcuts import get_object_or_404

from users.permissions import (
    IsAdminDoctorPatientReceptionist,
)

from audit.services import create_audit

from .models import Notification

from .serializers import NotificationSerializer


# ======================================================
# LISTAR NOTIFICACIONES
# ======================================================

@api_view(["GET"])
@permission_classes([
    IsAdminDoctorPatientReceptionist
])
def notifications_api(request):

    # ==================================================
    # SEGURIDAD
    # ==================================================
    #
    # Solo se permiten notificaciones pertenecientes
    # al usuario autenticado.
    # ==================================================

    notifications = Notification.objects.filter(
        user=request.user
    ).order_by(
        "-created_at"
    )


    # ==================================================
    # SERIALIZACIÓN
    # ==================================================

    serializer = NotificationSerializer(
        notifications,
        many=True
    )


    # ==================================================
    # AUDITORÍA
    # ==================================================

    create_audit(
        user=request.user,
        action="read",
        module="notifications",
        object_id=None,
        description=(
            f"El usuario {request.user.username} "
            f"consultó sus notificaciones."
        ),
        request=request
    )


    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )


# ======================================================
# CONTADOR DE NOTIFICACIONES NO LEÍDAS
# ======================================================

@api_view(["GET"])
@permission_classes([
    IsAdminDoctorPatientReceptionist
])
def unread_notifications_count_api(request):

    unread_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()


    # ==================================================
    # AUDITORÍA
    # ==================================================

    create_audit(
        user=request.user,
        action="read",
        module="notifications",
        object_id=None,
        description=(
            f"El usuario {request.user.username} "
            f"consultó el número de notificaciones "
            f"no leídas."
        ),
        request=request
    )


    return Response(
        {
            "unread_count": unread_count
        },
        status=status.HTTP_200_OK
    )


# ======================================================
# OBTENER UNA NOTIFICACIÓN
# ======================================================

@api_view(["GET"])
@permission_classes([
    IsAdminDoctorPatientReceptionist
])
def get_notification_api(
    request,
    notification_id
):

    # ==================================================
    # SEGURIDAD
    # ==================================================
    #
    # Solo se puede consultar una notificación que
    # pertenezca al usuario autenticado.
    # ==================================================

    notification = get_object_or_404(
        Notification,
        id=notification_id,
        user=request.user
    )


    # ==================================================
    # SERIALIZACIÓN
    # ==================================================

    serializer = NotificationSerializer(
        notification
    )


    # ==================================================
    # AUDITORÍA
    # ==================================================

    create_audit(
        user=request.user,
        action="read",
        module="notifications",
        object_id=notification.id,
        description=(
            f"El usuario {request.user.username} "
            f"consultó la notificación "
            f"con ID {notification.id}."
        ),
        request=request
    )


    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )


# ======================================================
# MARCAR NOTIFICACIÓN COMO LEÍDA
# ======================================================

@api_view(["PATCH"])
@permission_classes([
    IsAdminDoctorPatientReceptionist
])
def mark_notification_read_api(
    request,
    notification_id
):

    # ==================================================
    # SEGURIDAD
    # ==================================================
    #
    # El ID debe pertenecer al usuario autenticado.
    # ==================================================

    notification = get_object_or_404(
        Notification,
        id=notification_id,
        user=request.user
    )


    # ==================================================
    # ACTUALIZAR ESTADO
    # ==================================================

    notification.is_read = True

    notification.save(
        update_fields=[
            "is_read"
        ]
    )


    # ==================================================
    # AUDITORÍA
    # ==================================================

    create_audit(
        user=request.user,
        action="update",
        module="notifications",
        object_id=notification.id,
        description=(
            f"El usuario {request.user.username} "
            f"marcó como leída la notificación "
            f"con ID {notification.id}."
        ),
        request=request
    )


    # ==================================================
    # SERIALIZACIÓN
    # ==================================================

    serializer = NotificationSerializer(
        notification
    )


    return Response(
        {
            "message": (
                "Notificación marcada como leída."
            ),
            "notification": serializer.data
        },
        status=status.HTTP_200_OK
    )


# ======================================================
# MARCAR TODAS COMO LEÍDAS
# ======================================================

@api_view(["PATCH"])
@permission_classes([
    IsAdminDoctorPatientReceptionist
])
def mark_all_notifications_read_api(request):

    updated = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).update(
        is_read=True
    )


    # ==================================================
    # AUDITORÍA
    # ==================================================

    create_audit(
        user=request.user,
        action="update",
        module="notifications",
        object_id=None,
        description=(
            f"El usuario {request.user.username} "
            f"marcó {updated} notificación(es) "
            f"como leídas."
        ),
        request=request
    )


    return Response(
        {
            "message": (
                "Todas las notificaciones fueron "
                "marcadas como leídas."
            ),
            "updated": updated
        },
        status=status.HTTP_200_OK
    )


# ======================================================
# ELIMINAR NOTIFICACIÓN
# ======================================================

@api_view(["DELETE"])
@permission_classes([
    IsAdminDoctorPatientReceptionist
])
def delete_notification_api(
    request,
    notification_id
):

    # ==================================================
    # SEGURIDAD
    # ==================================================
    #
    # Solo se puede eliminar una notificación que
    # pertenezca al usuario autenticado.
    # ==================================================

    notification = get_object_or_404(
        Notification,
        id=notification_id,
        user=request.user
    )


    notification_id_deleted = notification.id


    # ==================================================
    # AUDITORÍA
    # ==================================================

    create_audit(
        user=request.user,
        action="delete",
        module="notifications",
        object_id=notification_id_deleted,
        description=(
            f"El usuario {request.user.username} "
            f"eliminó la notificación "
            f"con ID {notification_id_deleted}."
        ),
        request=request
    )


    # ==================================================
    # ELIMINAR
    # ==================================================

    notification.delete()


    return Response(
        {
            "message": (
                "Notificación eliminada correctamente."
            )
        },
        status=status.HTTP_200_OK
    )

