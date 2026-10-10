from django.contrib import admin

from .models import FAQ, ContactMessage, TeamMember


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "name", "email", "is_resolved", "created_at")
    list_filter = ("is_resolved",)
    list_editable = ("is_resolved",)
    readonly_fields = ("name", "email", "subject", "message", "created_at")


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "order", "is_active")
    list_editable = ("order", "is_active")


admin.site.register(TeamMember)
