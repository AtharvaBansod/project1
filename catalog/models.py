from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    country = models.CharField(max_length=80, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    icon = models.CharField(max_length=40, default="bi-gear", help_text="Bootstrap Icons class, e.g. bi-gear")
    description = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    class Kind(models.TextChoices):
        MACHINE = "machine", "Machine"
        SPARE = "spare", "Spare Part"

    class Stock(models.TextChoices):
        IN_STOCK = "in_stock", "In stock"
        LOW = "low", "Low stock"
        ON_ORDER = "on_order", "Available on order"
        OUT = "out", "Out of stock"

    kind = models.CharField(max_length=10, choices=Kind.choices, default=Kind.MACHINE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    sku = models.CharField("SKU / Part no.", max_length=60, unique=True)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="products")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    summary = models.CharField(max_length=250, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="products/", blank=True)
    indicative_price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        help_text="USD. Leave blank for price on request.")
    stock_status = models.CharField(max_length=10, choices=Stock.choices, default=Stock.IN_STOCK)
    stock_qty = models.PositiveIntegerField(default=0)
    lead_time_days = models.PositiveIntegerField(default=0, help_text="Delivery lead time when not in stock")
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    compatible_machines = models.ManyToManyField(
        "self", symmetrical=False, blank=True, related_name="compatible_parts",
        limit_choices_to={"kind": "machine"}, help_text="For spare parts: machines this part fits")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.sku}")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalog:detail", args=[self.slug])

    @property
    def stock_badge(self):
        return {"in_stock": "success", "low": "warning", "on_order": "info", "out": "secondary"}[self.stock_status]

    def __str__(self):
        return f"{self.name} ({self.sku})"


class Specification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="specs")
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=200)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.name}: {self.value}"


class Document(models.Model):
    class DocType(models.TextChoices):
        DATASHEET = "datasheet", "Datasheet"
        MANUAL = "manual", "Manual"

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="documents")
    doc_type = models.CharField(max_length=12, choices=DocType.choices, default=DocType.DATASHEET)
    title = models.CharField(max_length=150)
    file = models.FileField(upload_to="documents/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["doc_type", "title"]

    @property
    def is_public(self):
        return self.doc_type == self.DocType.DATASHEET

    def __str__(self):
        return self.title


class SavedProduct(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saved_products")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="saved_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")
        ordering = ["-created_at"]
