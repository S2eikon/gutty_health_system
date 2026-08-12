# ======================================================
# USERS / SERIALIZERS.PY
# GUTTY HEALTH SYSTEM
# ======================================================

from rest_framework import serializers
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError

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
            'phone',
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


# ======================================================
# SERIALIZADOR - REGISTRO DE USUARIO
# ======================================================

class RegisterSerializer(serializers.ModelSerializer):

    # ==================================================
    # CONFIRMAR CONTRASEÑA
    # ==================================================

    confirmPassword = serializers.CharField(
        write_only=True,
        style={
            'input_type': 'password'
        }
    )

    # ==================================================
    # CONFIGURACIÓN
    # ==================================================

    class Meta:

        model = User

        fields = [
            'first_name',
            'last_name',
            'username',
            'email',
            'phone',
            'password',
            'confirmPassword',
        ]

        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    # ==================================================
    # VALIDAR USERNAME
    # ==================================================

    def validate_username(self, value):

        if User.objects.filter(
            username=value
        ).exists():

            raise serializers.ValidationError(
                'Este username ya está registrado.'
            )

        return value

    # ==================================================
    # VALIDAR EMAIL
    # ==================================================

    def validate_email(self, value):

        if User.objects.filter(
            email=value
        ).exists():

            raise serializers.ValidationError(
                'Este correo electrónico ya está registrado.'
            )

        return value

    # ==================================================
    # VALIDAR DATOS DEL REGISTRO
    # ==================================================

    def validate(self, data):

        # ==============================================
        # OBTENER CONTRASEÑAS
        # ==============================================

        password = data.get(
            'password'
        )

        confirm_password = data.get(
            'confirmPassword'
        )

        # ==============================================
        # VALIDAR QUE LAS CONTRASEÑAS COINCIDAN
        # ==============================================

        if password != confirm_password:

            raise serializers.ValidationError({

                'confirmPassword':
                    'Las contraseñas no coinciden.'

            })

        # ==============================================
        # VALIDAR CONTRASEÑA CON DJANGO
        # ==============================================

        try:

            password_validation.validate_password(
                password=password
            )

        except ValidationError as error:

            raise serializers.ValidationError({

                'password':
                    list(error.messages)

            })

        return data

    # ==================================================
    # CREAR USUARIO
    # ==================================================

    def create(self, validated_data):

        # ==============================================
        # ELIMINAR CONFIRMACIÓN DE CONTRASEÑA
        # ==============================================

        validated_data.pop(
            'confirmPassword'
        )

        # ==============================================
        # OBTENER CONTRASEÑA
        # ==============================================

        password = validated_data.pop(
            'password'
        )

        # ==============================================
        # CREAR USUARIO
        # ==============================================

        user = User.objects.create_user(
            password=password,
            role='patient',
            **validated_data
        )

        return user