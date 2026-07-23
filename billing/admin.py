from django.contrib import admin
from .models import Bill

@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ('patient', 'concept', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('patient__username', 'concept')
