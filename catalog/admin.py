from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple

from .models import Brand, Category, Document, Product, SavedProduct, Specification


class SpecInline(admin.TabularInline):
    model = Specification
    extra = 3
    verbose_name = "specification"
    verbose_name_plural = "Specifications (name and value, one per row)"


class DocInline(admin.TabularInline):
    model = Document
    extra = 2
    verbose_name = "document"
    verbose_name_plural = "Datasheets and manuals (upload files here)"


class ProductAdminForm(forms.ModelForm):
    compatible_parts = forms.ModelMultipleChoiceField(
        queryset=Product.objects.filter(kind=Product.Kind.SPARE), required=False,
        widget=FilteredSelectMultiple("spare parts", False),
        label="Compatible spare parts", help_text="For machines: spare parts that fit this machine")

    class Meta:
        model = Product
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["compatible_parts"].initial = self.instance.compatible_parts.all()


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ("name", "sku", "kind", "brand", "category", "stock_status", "stock_qty", "is_featured", "is_active")
    list_editable = ("stock_status", "stock_qty", "is_featured", "is_active")
    list_filter = ("kind", "brand", "category", "stock_status", "is_featured")
    search_fields = ("name", "sku", "description")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("compatible_machines",)
    inlines = [SpecInline, DocInline]
    fieldsets = (
        ("Basic details", {"fields": ("kind", "name", "slug", "sku", "brand", "category", "summary", "description", "image")}),
        ("Price and stock", {"fields": ("indicative_price", "stock_status", "stock_qty", "lead_time_days")}),
        ("Compatibility", {
            "description": "Spare parts: choose the machines they fit. Machines: choose the spare parts that fit them.",
            "fields": ("compatible_machines", "compatible_parts")}),
        ("Visibility", {"fields": ("is_featured", "is_active")}),
    )

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        if form.instance.kind == Product.Kind.MACHINE:
            form.instance.compatible_parts.set(form.cleaned_data["compatible_parts"])


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "country")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "icon")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "product", "doc_type", "uploaded_at")
    list_filter = ("doc_type",)


admin.site.register(SavedProduct)
