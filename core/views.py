from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from catalog.models import Brand, Category, Product

from .forms import ContactForm
from .models import FAQ, ContactMessage, TeamMember


def home(request):
    active = Product.objects.filter(is_active=True).select_related("brand", "category")
    return render(request, "core/home.html", {
        "featured": active.filter(is_featured=True)[:6],
        "latest": active[:4],
        "categories": Category.objects.all(),
        "brands": Brand.objects.all(),
    })


def about(request):
    steps = [
        ("bi-search", "Browse", "Explore machines and spare parts with full specifications and datasheets."),
        ("bi-chat-dots", "Enquire", "Send a price, availability or compatibility enquiry in minutes."),
        ("bi-file-earmark-text", "Receive a quote", "Our team replies with a formal quotation and lead time."),
        ("bi-truck", "Import and install", "We handle import logistics, installation and training."),
    ]
    return render(request, "core/about.html", {"steps": steps, "team": TeamMember.objects.all()})


def contact(request):
    initial = {}
    if request.user.is_authenticated:
        initial = {"name": request.user.display_name, "email": request.user.email}
    form = ContactForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        contact_message = form.save(commit=False)
        if request.user.is_authenticated:
            contact_message.user = request.user
        contact_message.save()
        messages.success(request, "Thanks! Your message has been sent. We reply within one business day.")
        return redirect("core:contact")
    return render(request, "core/contact.html", {"form": form, "faqs": FAQ.objects.filter(is_active=True)})


@login_required
def my_messages(request):
    messages_sent = ContactMessage.objects.filter(user=request.user)
    return render(request, "core/my_messages.html", {"messages_sent": messages_sent})
