from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from enquiries.models import Enquiry
from services.models import ServiceRequest

from .decorators import role_required
from .forms import BuyerProfileForm, BuyerRegistrationForm, UserProfileForm
from .models import BuyerProfile, User


def register(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")
    form = BuyerRegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Welcome to IndustroLink! Your buyer account is ready.")
        return redirect("accounts:dashboard")
    return render(request, "accounts/register.html", {"form": form})


@login_required
def dashboard(request):
    user = request.user
    if user.is_admin_role:
        return redirect("admin:index")
    if user.is_technician:
        return redirect("services:technician_list")
    ctx = {
        "enquiry_count": Enquiry.objects.filter(user=user).count(),
        "saved_count": user.saved_products.count(),
        "service_count": ServiceRequest.objects.filter(buyer=user).count(),
        "recent_enquiries": Enquiry.objects.filter(user=user)[:5],
        "recent_services": ServiceRequest.objects.filter(buyer=user)[:5],
    }
    return render(request, "accounts/dashboard.html", ctx)


@role_required(User.Role.BUYER)
def profile(request):
    bp, _ = BuyerProfile.objects.get_or_create(user=request.user, defaults={"company_name": ""})
    uform = UserProfileForm(request.POST or None, instance=request.user)
    bform = BuyerProfileForm(request.POST or None, instance=bp)
    if request.method == "POST" and uform.is_valid() and bform.is_valid():
        uform.save()
        bform.save()
        messages.success(request, "Profile updated.")
        return redirect("accounts:profile")
    return render(request, "accounts/profile.html", {"uform": uform, "bform": bform})
