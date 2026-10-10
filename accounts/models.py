from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        BUYER = "buyer", "Buyer"
        TECHNICIAN = "technician", "Technician"
        ADMIN = "admin", "Admin"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.BUYER)
    phone = models.CharField(max_length=30, blank=True)

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = self.Role.ADMIN
        if self.role == self.Role.ADMIN:
            self.is_staff = True
        super().save(*args, **kwargs)

    @property
    def is_buyer(self):
        return self.role == self.Role.BUYER

    @property
    def is_technician(self):
        return self.role == self.Role.TECHNICIAN

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN

    @property
    def display_name(self):
        return self.get_full_name() or self.username


class BuyerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="buyer_profile")
    company_name = models.CharField(max_length=150)
    industry = models.CharField(max_length=100, blank=True)
    tax_id = models.CharField("GST / Tax ID", max_length=50, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=80, blank=True)
    country = models.CharField(max_length=80, blank=True)

    def __str__(self):
        return self.company_name


class TechnicianManager(UserManager):
    def get_queryset(self):
        return super().get_queryset().filter(role=User.Role.TECHNICIAN)


class Technician(User):
    objects = TechnicianManager()

    class Meta:
        proxy = True
        verbose_name = "technician"
        verbose_name_plural = "technicians"

    def save(self, *args, **kwargs):
        self.role = User.Role.TECHNICIAN
        super().save(*args, **kwargs)
