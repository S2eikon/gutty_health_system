from rest_framework import serializers
from .models import Bill

class BillSerializer(serializers.ModelSerializer):

    patient_name = serializers.SerializerMethodField()

    class Meta:
        model = Bill
        fields = [
            'id',
            'patient',
            'patient_name',
            'concept',
            'amount',
            'status',
            'created_at',
        ]
        read_only_fields = [
            'created_at',
            'patient_name',
        ]

    def get_patient_name(self, obj):
        return obj.patient.get_full_name() or obj.patient.username
