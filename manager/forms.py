from django import forms

from accounts.models import User
from core.models import ContactMessage
from enquiries.models import Enquiry
from services.models import ServiceRequest


class EnquiryReplyForm(forms.ModelForm):
    class Meta:
        model = Enquiry
        fields = ("status", "admin_response", "quotation")
        widgets = {"admin_response": forms.Textarea(attrs={"rows": 5})}
        labels = {"admin_response": "Reply to customer", "quotation": "Quotation file (PDF)"}


class ServiceAssignForm(forms.ModelForm):
    technician = forms.ModelChoiceField(
        queryset=User.objects.filter(role=User.Role.TECHNICIAN, is_active=True),
        required=False, empty_label="Not assigned")

    class Meta:
        model = ServiceRequest
        fields = ("technician", "status")


class MessageReplyForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ("reply", "is_resolved")
        widgets = {"reply": forms.Textarea(attrs={"rows": 5})}
        labels = {"reply": "Reply", "is_resolved": "Mark as resolved"}
