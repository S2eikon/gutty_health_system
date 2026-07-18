from rest_framework import serializers
from django.contrib.auth import password_validation
from .models import User

class UserProfileSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        style={'input_type': 'password'}
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
        read_only_fields = ['id', 'username', 'role']

    def validate_password(self, value):
        if value == '' or value is None:
            return value
        password_validation.validate_password(password=value, user=self.instance)
        return value

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        # Actualizar los demás campos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Si el usuario envió una nueva contraseña,
        # se cifra correctamente antes de guardar.
        if password:
            instance.set_password(password)

        # Guardar una sola vez
        instance.save()

        return instance
