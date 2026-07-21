from django.contrib import admin

from .models import MedicalRecord


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'patient',
        'consultation',
        'created_at'
    )

    list_filter = (
        'consultation',
        'created_at'
    )

    search_fields = (
        'patient__username',
        'diagnosis'
    )

    ordering = (
        '-created_at',
    )