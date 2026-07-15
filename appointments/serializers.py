from rest_framework import serializers
from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Appointment
        fields = "__all__"
        read_only_fields = ["patient"]

    def validate(self, data):

        if not data.get("appointment_type"):
            raise serializers.ValidationError({
                "appointment_type": "Este campo es obligatorio."
            })

        if not data.get("date"):
            raise serializers.ValidationError({
                "date": "Este campo es obligatorio."
            })

        if not data.get("time"):
            raise serializers.ValidationError({
                "time": "Este campo es obligatorio."
            })

        return data