from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):

    # ======================================================
    # TIPO DE NOTIFICACIÓN
    # ======================================================

    notification_type_display = serializers.CharField(
        source="get_notification_type_display",
        read_only=True
    )


    # ======================================================
    # INFORMACIÓN DEL USUARIO
    # ======================================================

    username = serializers.CharField(
        source="user.username",
        read_only=True
    )


    # ======================================================
    # CONFIGURACIÓN
    # ======================================================

    class Meta:

        model = Notification

        fields = [

            "id",

            # ----------------------------------------------
            # USUARIO
            # ----------------------------------------------

            "user",
            "username",

            # ----------------------------------------------
            # TIPO
            # ----------------------------------------------

            "notification_type",
            "notification_type_display",

            # ----------------------------------------------
            # CONTENIDO
            # ----------------------------------------------

            "title",
            "message",

            # ----------------------------------------------
            # CITA RELACIONADA
            # ----------------------------------------------

            "appointment_id",

            # ----------------------------------------------
            # ESTADO
            # ----------------------------------------------

            "is_read",

            # ----------------------------------------------
            # FECHA
            # ----------------------------------------------

            "created_at",

        ]


        # ==================================================
        # CAMPOS DE SOLO LECTURA
        # ==================================================

        read_only_fields = [

            "id",

            "user",

            "username",

            "notification_type",

            "notification_type_display",

            "title",

            "message",

            "appointment_id",

            "created_at",

        ]


    # ======================================================
    # REPRESENTACIÓN
    # ======================================================

    def to_representation(
        self,
        instance
    ):

        data = super().to_representation(
            instance
        )

        return data

