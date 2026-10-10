from django.contrib import admin

from .models import ServiceRequest


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ("reference", "service_type", "buyer", "product", "technician", "status", "preferred_date")
    list_filter = ("status", "service_type", "technician")
    list_editable = ("technician", "status")
    search_fields = ("reference", "buyer__username", "buyer__email", "site_address")
    readonly_fields = ("reference", "created_at", "updated_at")
