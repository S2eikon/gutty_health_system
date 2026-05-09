from rest_framework import serializers
from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Appointment
        fields = '__all__'

    def validate(self, data):
        # Solo validación básica (Django ya valida el resto)
        if not data.get('appointment_type'):
            raise serializers.ValidationError("appointment_type es obligatorio")

        if not data.get('date'):
            raise serializers.ValidationError("date es obligatorio")

        if not data.get('time'):
            raise serializers.ValidationError("time es obligatorio")

        return data