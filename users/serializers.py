from rest_framework import serializers
from django.contrib.auth import password_validation

from .models import User


# ======================================================
# SERIALIZADOR - PERFIL DE USUARIO
# ======================================================

class UserProfileSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        style={
            'input_type': 'password'
        }
    )

    class Meta:

        model = User

        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'role',
            'password',
        ]

        read_only_fields = [
            'id',
            'username',
            'role',
        ]

    # ==================================================
    # VALIDAR CONTRASEÑA
    # ==================================================

    def validate_password(self, value):

        if value == '' or value is None:

            return value

        password_validation.validate_password(
            password=value,
            user=self.instance
        )

        return value

    # ==================================================
    # ACTUALIZAR PERFIL
    # ==================================================

    def update(
        self,
        instance,
        validated_data
    ):

        password = validated_data.pop(
            'password',
            None
        )

        # ==============================================
        # ACTUALIZAR DATOS DEL PERFIL
        # ==============================================

        for attr, value in validated_data.items():

            setattr(
                instance,
                attr,
                value
            )

        # ==============================================
        # ACTUALIZAR CONTRASEÑA
        # ==============================================

        if password:

            instance.set_password(
                password
            )

        instance.save()

        return instance


# ======================================================
# SERIALIZADOR - USUARIOS / PACIENTES
# ======================================================

class UserSerializer(serializers.ModelSerializer):

    full_name = serializers.SerializerMethodField()

    class Meta:

        model = User

        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'full_name'
        ]

    # ==================================================
    # OBTENER NOMBRE COMPLETO
    # ==================================================

    def get_full_name(self, obj):

        return (
            f"{obj.first_name} "
            f"{obj.last_name}"
        ).strip()

