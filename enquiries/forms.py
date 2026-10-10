from django import forms

from catalog.models import Product

from .models import Enquiry


class EnquiryForm(forms.ModelForm):
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(is_active=True), required=False, empty_label="General / not listed")

    class Meta:
        model = Enquiry
        fields = ("product", "quantity", "name", "email", "phone", "company", "message")
        widgets = {"message": forms.Textarea(attrs={"rows": 4})}

    def clean_quantity(self):
        qty = self.cleaned_data["quantity"]
        if qty < 1:
            raise forms.ValidationError("Quantity must be at least 1.")
        return qty
