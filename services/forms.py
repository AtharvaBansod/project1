import datetime

from django import forms

from catalog.models import Product

from .models import ServiceRequest


class ServiceRequestForm(forms.ModelForm):
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(kind="machine", is_active=True), required=False,
        empty_label="Not listed / other equipment")

    class Meta:
        model = ServiceRequest
        fields = ("service_type", "product", "site_address", "preferred_date", "description")
        widgets = {
            "preferred_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_preferred_date(self):
        d = self.cleaned_data.get("preferred_date")
        if d and d < datetime.date.today():
            raise forms.ValidationError("Preferred date cannot be in the past.")
        return d


class TechnicianUpdateForm(forms.ModelForm):
    status = forms.ChoiceField(choices=[
        (ServiceRequest.Status.ASSIGNED, "Technician assigned"),
        (ServiceRequest.Status.IN_PROGRESS, "In progress"),
        (ServiceRequest.Status.COMPLETED, "Completed"),
    ])

    class Meta:
        model = ServiceRequest
        fields = ("status", "technician_notes")
        widgets = {"technician_notes": forms.Textarea(attrs={"rows": 4})}
