from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Brand, Category, Document, Product, SavedProduct


def product_list(request):
    qs = Product.objects.filter(is_active=True).select_related("brand", "category")
    kind = request.GET.get("kind", "")
    brand = request.GET.get("brand", "")
    category = request.GET.get("category", "")
    q = request.GET.get("q", "").strip()
    if kind in ("machine", "spare"):
        qs = qs.filter(kind=kind)
    if brand:
        qs = qs.filter(brand__slug=brand)
    if category:
        qs = qs.filter(category__slug=category)
    if q:
        qs = qs.filter(
            Q(name__icontains=q) | Q(sku__icontains=q) | Q(description__icontains=q) | Q(brand__name__icontains=q))
    page = Paginator(qs, 9).get_page(request.GET.get("page"))
    params = request.GET.copy()
    params.pop("page", None)
    return render(request, "catalog/product_list.html", {
        "page": page, "brands": Brand.objects.all(), "categories": Category.objects.all(),
        "kind": kind, "brand": brand, "category": category, "q": q, "qs": params.urlencode(),
    })


def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related("brand", "category"), slug=slug, is_active=True)
    related = Product.objects.filter(is_active=True, category=product.category).exclude(pk=product.pk)[:3]
    saved = request.user.is_authenticated and product.saved_by.filter(user=request.user).exists()
    compat = product.compatible_machines.all() if product.kind == "spare" else product.compatible_parts.all()
    return render(request, "catalog/product_detail.html", {
        "product": product, "related": related, "saved": saved, "compat": compat,
    })


@login_required
@require_POST
def toggle_save(request, slug):
    product = get_object_or_404(Product, slug=slug)
    obj, created = SavedProduct.objects.get_or_create(user=request.user, product=product)
    if created:
        messages.success(request, f"Saved {product.name}.")
    else:
        obj.delete()
        messages.info(request, f"Removed {product.name} from saved products.")
    nxt = request.POST.get("next", "")
    return redirect(nxt if nxt.startswith("/") and not nxt.startswith("//") else product.get_absolute_url())


@login_required
def saved_products(request):
    items = SavedProduct.objects.filter(user=request.user).select_related("product__brand", "product__category")
    return render(request, "catalog/saved.html", {"items": items})


def technical(request):
    q = request.GET.get("q", "").strip()
    docs = Document.objects.select_related("product__brand")
    if q:
        docs = docs.filter(Q(title__icontains=q) | Q(product__name__icontains=q) | Q(product__sku__icontains=q))
    machines = Product.objects.filter(kind="machine", is_active=True).prefetch_related("compatible_parts")
    return render(request, "catalog/technical.html", {
        "datasheets": docs.filter(doc_type="datasheet"),
        "manuals": docs.filter(doc_type="manual"),
        "machines": machines, "q": q,
    })


def document_download(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    if not doc.is_public and not request.user.is_authenticated:
        messages.warning(request, "Please sign in to download manuals.")
        return redirect(f"/accounts/login/?next={request.path}")
    try:
        return FileResponse(doc.file.open("rb"), as_attachment=True, filename=doc.file.name.split("/")[-1])
    except FileNotFoundError:
        raise Http404("File not found")
