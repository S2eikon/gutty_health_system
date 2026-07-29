from django.contrib import admin

from .models import MedicalDocument


@admin.register(MedicalDocument)
class MedicalDocumentAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "title",
        "patient",
        "uploaded_by",
        "document_type",
        "uploaded_at",
    )

    list_filter = (
        "document_type",
        "uploaded_at",
    )

    search_fields = (
        "title",
        "patient__username",
        "patient__first_name",
        "patient__last_name",
        "uploaded_by__username",
    )

    readonly_fields = (
        "uploaded_at",
    )

    ordering = (
        "-uploaded_at",
    )

    fieldsets = (

        (
            "Información del documento",
            {
                "fields": (
                    "title",
                    "description",
                    "document_type",
                    "file",
                )
            },
        ),

        (
            "Paciente",
            {
                "fields": (
                    "patient",
                )
            },
        ),

        (
            "Subido por",
            {
                "fields": (
                    "uploaded_by",
                    "uploaded_at",
                )
            },
        ),

    )