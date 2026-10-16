from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.decorators import role_required
from accounts.models import User

from .forms import ServiceRequestForm, TechnicianUpdateForm
from .models import ServiceRequest

SERVICES = [
    {"key": "installation", "title": "Installation", "icon": "bi-tools",
     "text": "Site survey, commissioning and handover by factory-trained engineers.",
     "points": ["Foundation and utility checklist", "On-site commissioning and test run", "Operator handover"]},
    {"key": "maintenance", "title": "Maintenance", "icon": "bi-wrench-adjustable",
     "text": "Preventive maintenance plans and genuine spare part replacement.",
     "points": ["Quarterly or annual plans", "Genuine spare parts", "Remote diagnostics support"]},
    {"key": "warranty", "title": "Warranty", "icon": "bi-shield-check",
     "text": "12-24 month manufacturer warranty on machines, 6 months on spare parts.",
     "points": ["Fast claim handling", "Replacement part dispatch", "Transparent coverage terms"]},
    {"key": "training", "title": "Training", "icon": "bi-mortarboard",
     "text": "Operator and maintenance team training on site or online.",
     "points": ["Safety and operation basics", "Troubleshooting workshops", "Certificate of completion"]},
]


def service_list(request):
    return render(request, "services/services.html", {"services": SERVICES})


@role_required(User.Role.BUYER)
def request_create(request):
    initial = {"service_type": request.GET.get("type", "installation")}
    profile = getattr(request.user, "buyer_profile", None)
    if profile and profile.address:
        initial["site_address"] = profile.address
    form = ServiceRequestForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        sr = form.save(commit=False)
        sr.buyer = request.user
        sr.save()
        messages.success(request, f"Service request {sr.reference} submitted.")
        return redirect("services:buyer_list")
    return render(request, "services/request_form.html", {"form": form})


@role_required(User.Role.BUYER)
def buyer_list(request):
    return render(request, "services/buyer_list.html", {
        "requests": ServiceRequest.objects.filter(buyer=request.user).select_related("product", "technician")})


@role_required(User.Role.TECHNICIAN)
def technician_list(request):
    scope = request.GET.get("scope", "mine")
    status = request.GET.get("status", "")
    if scope == "open":
        qs = ServiceRequest.objects.filter(technician__isnull=True, status=ServiceRequest.Status.NEW)
    else:
        qs = ServiceRequest.objects.filter(technician=request.user)
        if status:
            qs = qs.filter(status=status)
    return render(request, "services/technician_list.html", {
        "requests": qs.select_related("product", "buyer"), "status": status, "scope": scope,
        "statuses": ServiceRequest.Status.choices,
        "open_count": ServiceRequest.objects.filter(technician__isnull=True, status=ServiceRequest.Status.NEW).count()})


@role_required(User.Role.TECHNICIAN)
@require_POST
def technician_claim(request, pk):
    sr = get_object_or_404(ServiceRequest, pk=pk, technician__isnull=True, status=ServiceRequest.Status.NEW)
    sr.technician = request.user
    sr.save()
    messages.success(request, f"{sr.reference} is now assigned to you.")
    return redirect("services:technician_list")


@role_required(User.Role.TECHNICIAN)
def technician_update(request, pk):
    sr = get_object_or_404(ServiceRequest, pk=pk, technician=request.user)
    form = TechnicianUpdateForm(request.POST or None, instance=sr)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"{sr.reference} updated.")
        return redirect("services:technician_list")
    return render(request, "services/technician_update.html", {"sr": sr, "form": form})
