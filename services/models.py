from django.conf import settings
from django.db import models


class ServiceRequest(models.Model):
    class Type(models.TextChoices):
        INSTALLATION = "installation", "Installation"
        MAINTENANCE = "maintenance", "Maintenance"
        WARRANTY = "warranty", "Warranty claim"
        TRAINING = "training", "Training"

    class Status(models.TextChoices):
        NEW = "new", "New"
        ASSIGNED = "assigned", "Technician assigned"
        IN_PROGRESS = "in_progress", "In progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    reference = models.CharField(max_length=20, unique=True, editable=False, blank=True)
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="service_requests")
    product = models.ForeignKey("catalog.Product", null=True, blank=True, on_delete=models.SET_NULL)
    service_type = models.CharField(max_length=20, choices=Type.choices, default=Type.INSTALLATION)
    description = models.TextField()
    site_address = models.CharField(max_length=250)
    preferred_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.NEW)
    technician = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="assigned_services", limit_choices_to={"role": "technician"})
    technician_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if self.technician and self.status == self.Status.NEW:
            self.status = self.Status.ASSIGNED
        super().save(*args, **kwargs)
        if not self.reference:
            self.reference = f"SVC-{self.pk:05d}"
            super().save(update_fields=["reference"])

    @property
    def status_badge(self):
        return {"new": "secondary", "assigned": "info", "in_progress": "warning",
                "completed": "success", "cancelled": "dark"}[self.status]

    def __str__(self):
        return f"{self.reference} - {self.get_service_type_display()}"
