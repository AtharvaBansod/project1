from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import BuyerProfile, User


class BuyerRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=60)
    last_name = forms.CharField(max_length=60)
    email = forms.EmailField()
    phone = forms.CharField(max_length=30, required=False)
    company_name = forms.CharField(max_length=150)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "phone")

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.BUYER
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            BuyerProfile.objects.create(user=user, company_name=self.cleaned_data["company_name"])
        return user


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "phone")


class BuyerProfileForm(forms.ModelForm):
    class Meta:
        model = BuyerProfile
        fields = ("company_name", "industry", "tax_id", "address", "city", "country")
        widgets = {"address": forms.Textarea(attrs={"rows": 2})}
