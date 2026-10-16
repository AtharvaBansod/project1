from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import role_required
from accounts.models import User
from core.models import ContactMessage
from enquiries.models import Enquiry
from services.models import ServiceRequest

from .forms import EnquiryReplyForm, MessageReplyForm, ServiceAssignForm

admin_only = role_required(User.Role.ADMIN)


def notify(to_email, subject, body):
    send_mail(subject, body, "noreply@industrolink.example", [to_email], fail_silently=True)


@admin_only
def index(request):
    context = {
        "new_enquiries": Enquiry.objects.filter(status=Enquiry.Status.NEW).count(),
        "open_enquiries": Enquiry.objects.exclude(status=Enquiry.Status.CLOSED).count(),
        "new_services": ServiceRequest.objects.filter(status=ServiceRequest.Status.NEW).count(),
        "open_services": ServiceRequest.objects.exclude(
            status__in=[ServiceRequest.Status.COMPLETED, ServiceRequest.Status.CANCELLED]).count(),
        "open_messages": ContactMessage.objects.filter(is_resolved=False).count(),
        "recent_enquiries": Enquiry.objects.all()[:5],
        "recent_services": ServiceRequest.objects.select_related("buyer")[:5],
        "recent_messages": ContactMessage.objects.all()[:5],
    }
    return render(request, "manager/index.html", context)


@admin_only
def enquiry_list(request):
    qs = Enquiry.objects.select_related("product", "user")
    status = request.GET.get("status", "")
    q = request.GET.get("q", "").strip()
    if status:
        qs = qs.filter(status=status)
    if q:
        qs = qs.filter(Q(reference__icontains=q) | Q(name__icontains=q) | Q(email__icontains=q) | Q(company__icontains=q))
    return render(request, "manager/enquiry_list.html", {
        "enquiries": qs, "status": status, "q": q, "statuses": Enquiry.Status.choices})


@admin_only
def enquiry_detail(request, reference):
    enquiry = get_object_or_404(Enquiry, reference=reference)
    form = EnquiryReplyForm(request.POST or None, request.FILES or None, instance=enquiry)
    if request.method == "POST" and form.is_valid():
        form.save()
        if enquiry.admin_response:
            notify(enquiry.email, f"Your enquiry {enquiry.reference}",
                   f"Hello {enquiry.name},\n\n{enquiry.admin_response}\n\nStatus: {enquiry.get_status_display()}\n"
                   f"Reference: {enquiry.reference}")
        messages.success(request, f"{enquiry.reference} updated.")
        return redirect("manager:enquiry_detail", reference=enquiry.reference)
    return render(request, "manager/enquiry_detail.html", {"enquiry": enquiry, "form": form})


@admin_only
def service_list(request):
    qs = ServiceRequest.objects.select_related("buyer", "product", "technician")
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)
    return render(request, "manager/service_list.html", {
        "requests": qs, "status": status, "statuses": ServiceRequest.Status.choices})


@admin_only
def service_detail(request, pk):
    service = get_object_or_404(ServiceRequest.objects.select_related("buyer", "product", "technician"), pk=pk)
    form = ServiceAssignForm(request.POST or None, instance=service)
    if request.method == "POST" and form.is_valid():
        service = form.save()
        messages.success(request, f"{service.reference} updated.")
        return redirect("manager:service_detail", pk=service.pk)
    return render(request, "manager/service_detail.html", {"service": service, "form": form})


@admin_only
def message_list(request):
    qs = ContactMessage.objects.all()
    state = request.GET.get("state", "")
    if state == "open":
        qs = qs.filter(is_resolved=False)
    elif state == "resolved":
        qs = qs.filter(is_resolved=True)
    return render(request, "manager/message_list.html", {"messages_list": qs, "state": state})


@admin_only
def message_detail(request, pk):
    contact_message = get_object_or_404(ContactMessage, pk=pk)
    form = MessageReplyForm(request.POST or None, instance=contact_message)
    if request.method == "POST" and form.is_valid():
        updated = form.save(commit=False)
        if updated.reply and "reply" in form.changed_data:
            updated.replied_at = timezone.now()
            notify(updated.email, f"Re: {updated.subject}",
                   f"Hello {updated.name},\n\n{updated.reply}\n\n{settings.SITE_NAME} support")
        updated.save()
        messages.success(request, "Message updated.")
        return redirect("manager:message_detail", pk=updated.pk)
    return render(request, "manager/message_detail.html", {"item": contact_message, "form": form})
