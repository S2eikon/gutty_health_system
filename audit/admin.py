from django.contrib import admin

from .models import AuditLog



@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):


    # ==========================================
    # COLUMNAS VISIBLES
    # ==========================================

    list_display = (

        "id",

        "user",

        "action",

        "module",

        "object_id",

        "ip_address",

        "created_at",

    )


    # ==========================================
    # FILTROS LATERALES
    # ==========================================

    list_filter = (

        "action",

        "module",

        "created_at",

    )


    # ==========================================
    # BUSCADOR
    # ==========================================

    search_fields = (

        "user__username",

        "description",

        "module",

    )


    # ==========================================
    # ORDENAMIENTO
    # ==========================================

    ordering = (

        "-created_at",

    )


    # ==========================================
    # CAMPOS SOLO LECTURA
    # ==========================================

    readonly_fields = (

        "user",

        "action",

        "module",

        "object_id",

        "description",

        "ip_address",

        "created_at",

    )