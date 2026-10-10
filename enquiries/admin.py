from django.contrib import admin

from .models import Enquiry


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ("reference", "enquiry_type", "name", "company", "product", "status", "created_at")
    list_filter = ("status", "enquiry_type")
    list_editable = ("status",)
    search_fields = ("reference", "name", "email", "company", "product__name")
    readonly_fields = ("reference", "user", "created_at", "updated_at")
    fieldsets = (
        ("Enquiry", {"fields": ("reference", "enquiry_type", "user", "product", "quantity", "message", "created_at")}),
        ("Contact", {"fields": ("name", "email", "phone", "company")}),
        ("Response", {"fields": ("status", "admin_response", "quotation")}),
    )
