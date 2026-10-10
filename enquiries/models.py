from django.conf import settings
from django.db import models


class Enquiry(models.Model):
    class Type(models.TextChoices):
        PRICE = "price", "Price Enquiry"
        AVAILABILITY = "availability", "Availability Check"
        COMPATIBILITY = "compatibility", "Spare Part Compatibility"

    class Status(models.TextChoices):
        NEW = "new", "New"
        IN_PROGRESS = "in_progress", "In progress"
        QUOTED = "quoted", "Quotation sent"
        CLOSED = "closed", "Closed"

    reference = models.CharField(max_length=20, unique=True, editable=False, blank=True)
    enquiry_type = models.CharField(max_length=20, choices=Type.choices, default=Type.PRICE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                             related_name="enquiries")
    product = models.ForeignKey("catalog.Product", null=True, blank=True, on_delete=models.SET_NULL,
                                related_name="enquiries")
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    company = models.CharField(max_length=150, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    message = models.TextField()
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.NEW)
    admin_response = models.TextField(blank=True)
    quotation = models.FileField(upload_to="quotations/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "enquiries"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.reference:
            self.reference = f"ENQ-{self.pk:05d}"
            super().save(update_fields=["reference"])

    def __str__(self):
        return f"{self.reference} - {self.get_enquiry_type_display()}"
