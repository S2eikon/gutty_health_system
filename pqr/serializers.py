from rest_framework import serializers

from .models import PQR


class PQRSerializer(serializers.ModelSerializer):

    # ==========================================
    # INFORMACIÓN DEL PACIENTE
    # ==========================================

    user_name = serializers.CharField(
        source="user.get_full_name",
        read_only=True
    )

    username = serializers.CharField(
        source="user.username",
        read_only=True
    )

    # ==========================================
    # ADMINISTRADOR
    # ==========================================

    responded_by_name = serializers.SerializerMethodField()

    # ==========================================
    # NOMBRES LEGIBLES
    # ==========================================

    pqr_type_display = serializers.CharField(
        source="get_pqr_type_display",
        read_only=True
    )

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True
    )

    class Meta:

        model = PQR

        fields = [

            "id",

            "user",
            "user_name",
            "username",

            "pqr_type",
            "pqr_type_display",

            "subject",
            "message",

            "response",

            "status",
            "status_display",

            "responded_by",
            "responded_by_name",

            "created_at",
            "updated_at",
            "responded_at",

        ]

        read_only_fields = [

            "user",
            "response",
            "status",
            "responded_by",
            "responded_at",
            "created_at",
            "updated_at",

        ]

    # ==========================================
    # ADMINISTRADOR
    # ==========================================

    def get_responded_by_name(self, obj):

        if obj.responded_by:

            full_name = obj.responded_by.get_full_name()

            if full_name:
                return full_name

            return obj.responded_by.username

        return None