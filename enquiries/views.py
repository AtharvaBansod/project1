from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render

from catalog.models import Product

from .forms import EnquiryForm
from .models import Enquiry

TYPE_HELP = {
    "price": "Request a price quotation for a machine or spare part.",
    "availability": "Check current stock or lead time before you order.",
    "compatibility": "Confirm a spare part fits your machine model.",
}


def enquiry_create(request):
    etype = request.GET.get("type", "price")
    if etype not in Enquiry.Type.values:
        etype = "price"
    initial = {}
    user = request.user
    if user.is_authenticated:
        initial = {"name": user.display_name, "email": user.email, "phone": user.phone}
        profile = getattr(user, "buyer_profile", None)
        if profile:
            initial["company"] = profile.company_name
    product = Product.objects.filter(slug=request.GET.get("product", "")).first()
    if product:
        initial["product"] = product

    form = EnquiryForm(request.POST or None, initial=initial)
    if request.method == "POST":
        etype = request.POST.get("enquiry_type", etype)
        if etype not in Enquiry.Type.values:
            etype = "price"
        if form.is_valid():
            enq = form.save(commit=False)
            enq.enquiry_type = etype
            if user.is_authenticated:
                enq.user = user
            enq.save()
            return redirect("enquiries:success", reference=enq.reference)
    return render(request, "enquiries/enquiry_form.html", {
        "form": form, "etype": etype, "types": Enquiry.Type.choices, "help": TYPE_HELP[etype],
    })


def enquiry_success(request, reference):
    enq = get_object_or_404(Enquiry, reference=reference)
    return render(request, "enquiries/success.html", {"enquiry": enq})


@login_required
def enquiry_history(request):
    return render(request, "enquiries/history.html", {"enquiries": Enquiry.objects.filter(user=request.user)})


@login_required
def enquiry_detail(request, reference):
    enq = get_object_or_404(Enquiry, reference=reference, user=request.user)
    return render(request, "enquiries/detail.html", {"enquiry": enq})


@login_required
def quotation_download(request, reference):
    enq = get_object_or_404(Enquiry, reference=reference, user=request.user)
    if not enq.quotation:
        raise Http404("No quotation uploaded yet")
    return FileResponse(enq.quotation.open("rb"), as_attachment=True, filename=enq.quotation.name.split("/")[-1])
