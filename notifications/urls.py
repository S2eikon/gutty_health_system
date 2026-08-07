from django.urls import path

from . import views


# ======================================================
# URLS - NOTIFICACIONES
# ======================================================

urlpatterns = [

    # ==================================================
    # LISTAR NOTIFICACIONES
    # GET /notifications/api/
    # ==================================================

    path(
        "api/",
        views.notifications_api,
        name="notifications_api"
    ),


    # ==================================================
    # CONTADOR DE NOTIFICACIONES NO LEÍDAS
    # GET /notifications/api/unread-count/
    # ==================================================

    path(
        "api/unread-count/",
        views.unread_notifications_count_api,
        name="unread_notifications_count"
    ),


    # ==================================================
    # OBTENER UNA NOTIFICACIÓN
    # GET /notifications/api/<id>/
    # ==================================================

    path(
        "api/<int:notification_id>/",
        views.get_notification_api,
        name="get_notification"
    ),


    # ==================================================
    # MARCAR TODAS COMO LEÍDAS
    # PATCH /notifications/api/read-all/
    # ==================================================

    path(
        "api/read-all/",
        views.mark_all_notifications_read_api,
        name="mark_all_notifications_read"
    ),


    # ==================================================
    # MARCAR NOTIFICACIÓN COMO LEÍDA
    # PATCH /notifications/api/<id>/read/
    # ==================================================

    path(
        "api/<int:notification_id>/read/",
        views.mark_notification_read_api,
        name="mark_notification_read"
    ),


    # ==================================================
    # ELIMINAR NOTIFICACIÓN
    # DELETE /notifications/api/<id>/delete/
    # ==================================================

    path(
        "api/<int:notification_id>/delete/",
        views.delete_notification_api,
        name="delete_notification"
    ),

]

