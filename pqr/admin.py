from django.contrib import admin

from .models import PQR


@admin.register(PQR)
class PQRAdmin(admin.ModelAdmin):

    # ==========================================
    # COLUMNAS
    # ==========================================

    list_display = (

        "id",

        "subject",

        "user",

        "pqr_type",

        "status",

        "responded_by",

        "created_at",

        "responded_at",

    )

    # ==========================================
    # FILTROS
    # ==========================================

    list_filter = (

        "status",

        "pqr_type",

        "created_at",

        "responded_at",

    )

    # ==========================================
    # BUSCADOR
    # ==========================================

    search_fields = (

        "subject",

        "message",

        "response",

        "user__username",

        "user__first_name",

        "user__last_name",

    )

    # ==========================================
    # ORDEN
    # ==========================================

    ordering = (

        "-created_at",

    )

    # ==========================================
    # SOLO LECTURA
    # ==========================================

    readonly_fields = (

        "created_at",

        "updated_at",

        "responded_at",

    )

    # ==========================================
    # ORGANIZACIÓN DEL FORMULARIO
    # ==========================================

    fieldsets = (

        (

            "Información de la PQR",

            {

                "fields": (

                    "user",

                    "pqr_type",

                    "subject",

                    "message",

                )

            },

        ),

        (

            "Gestión",

            {

                "fields": (

                    "status",

                    "response",

                    "responded_by",

                )

            },

        ),

        (

            "Fechas",

            {

                "fields": (

                    "created_at",

                    "updated_at",

                    "responded_at",

                )

            },

        ),

    )