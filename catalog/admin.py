from django.contrib import admin

from .models import Brand, Category, Document, Product, SavedProduct, Specification


class SpecInline(admin.TabularInline):
    model = Specification
    extra = 1


class DocInline(admin.TabularInline):
    model = Document
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "kind", "brand", "category", "stock_status", "stock_qty", "is_featured", "is_active")
    list_editable = ("stock_status", "stock_qty", "is_featured", "is_active")
    list_filter = ("kind", "brand", "category", "stock_status", "is_featured")
    search_fields = ("name", "sku", "description")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("compatible_machines",)
    inlines = [SpecInline, DocInline]


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
