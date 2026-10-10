from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import BuyerProfile, Technician, User


class BuyerProfileInline(admin.StackedInline):
    model = BuyerProfile
    extra = 0


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "is_active")
    list_filter = ("role", "is_active")
    fieldsets = UserAdmin.fieldsets + (("Role", {"fields": ("role", "phone")}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Role", {"fields": ("role", "email", "phone")}),)
    inlines = [BuyerProfileInline]


@admin.register(Technician)
class TechnicianAdmin(UserAdmin):
    list_display = ("username", "first_name", "last_name", "email", "phone", "is_active")
    list_filter = ("is_active",)
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email", "phone")}),
        ("Access", {"fields": ("is_active",)}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("username", "first_name", "last_name", "email", "phone",
                                                   "password1", "password2")}),
    )

    def save_model(self, request, obj, form, change):
        obj.role = User.Role.TECHNICIAN
        obj.is_staff = False
        obj.is_superuser = False
        super().save_model(request, obj, form, change)
