from django import forms

from .i18n import t
from .models import Customer, Inquiry
from .utils import phone_digits

INPUT_CLASS = "field-input"


class HoneypotMixin(forms.Form):
    """Shared honeypot field; real users never see it."""

    website = forms.CharField(
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={
                "class": "hp-input",
                "tabindex": "-1",
                "autocomplete": "off",
                "aria-hidden": "true",
            }
        ),
    )

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise forms.ValidationError(t("err_invalid_request"))
        return ""


class InquiryForm(HoneypotMixin, forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ["name", "company", "phone", "email", "machine", "message"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                    "autocomplete": "name",
                    "maxlength": 120,
                }
            ),
            "company": forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                    "autocomplete": "organization",
                    "maxlength": 160,
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                    "inputmode": "tel",
                    "autocomplete": "tel",
                    "dir": "ltr",
                    "maxlength": 30,
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": INPUT_CLASS,
                    "inputmode": "email",
                    "autocomplete": "email",
                    "dir": "ltr",
                    "maxlength": 254,
                }
            ),
            "machine": forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                    "autocomplete": "off",
                    "maxlength": 120,
                }
            ),
            "message": forms.Textarea(
                attrs={"class": INPUT_CLASS, "rows": 4, "maxlength": 2000}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        labels = {
            "name": "f_name",
            "company": "f_company",
            "phone": "f_phone",
            "email": "f_email",
            "machine": "f_machine",
            "message": "f_message",
        }
        placeholders = {
            "name": "ph_name",
            "company": "ph_company",
            "phone": "ph_phone",
            "email": None,
            "machine": "ph_machine",
            "message": "ph_message",
        }
        for name, key in labels.items():
            self.fields[name].label = t(key)
            if placeholders[name]:
                self.fields[name].widget.attrs["placeholder"] = t(placeholders[name])
        self.fields["email"].widget.attrs["placeholder"] = "name@example.com"

    def clean_name(self):
        return " ".join(self.cleaned_data["name"].split())

    def clean_company(self):
        return " ".join(self.cleaned_data.get("company", "").split())

    def clean_phone(self):
        phone = phone_digits(self.cleaned_data["phone"])
        if not 8 <= len(phone) <= 15:
            raise forms.ValidationError(t("err_phone"))
        return phone

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()

    def clean_message(self):
        message = self.cleaned_data["message"].strip()
        if len(message) < 5:
            raise forms.ValidationError(t("err_message_short"))
        if len(message) > 2000:
            raise forms.ValidationError(t("err_message_long"))
        return message


class ClubSignupForm(HoneypotMixin, forms.ModelForm):
    """Customer club membership request; activated after admin approval."""

    class Meta:
        model = Customer
        fields = ["first_name", "last_name", "company", "phone", "email"]
        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": INPUT_CLASS, "autocomplete": "given-name", "maxlength": 60}
            ),
            "last_name": forms.TextInput(
                attrs={"class": INPUT_CLASS, "autocomplete": "family-name", "maxlength": 60}
            ),
            "company": forms.TextInput(
                attrs={"class": INPUT_CLASS, "autocomplete": "organization", "maxlength": 160}
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                    "inputmode": "tel",
                    "autocomplete": "tel",
                    "dir": "ltr",
                    "maxlength": 20,
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": INPUT_CLASS,
                    "inputmode": "email",
                    "autocomplete": "email",
                    "dir": "ltr",
                    "maxlength": 254,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        labels = {
            "first_name": "f_first_name",
            "last_name": "f_last_name",
            "company": "f_company_short",
            "phone": "f_phone",
            "email": "f_email",
        }
        placeholders = {
            "first_name": "ph_first",
            "last_name": "ph_last",
            "company": "ph_company",
            "phone": "ph_phone",
            "email": None,
        }
        for name, key in labels.items():
            self.fields[name].label = t(key)
            if placeholders[name]:
                self.fields[name].widget.attrs["placeholder"] = t(placeholders[name])
        self.fields["email"].widget.attrs["placeholder"] = "name@example.com"
        # The duplicate-number message must follow the active language
        self.fields["phone"].error_messages["unique"] = t("err_phone_duplicate")

    def clean_first_name(self):
        return " ".join(self.cleaned_data["first_name"].split())

    def clean_last_name(self):
        return " ".join(self.cleaned_data["last_name"].split())

    def clean_company(self):
        return " ".join(self.cleaned_data.get("company", "").split())

    def clean_phone(self):
        phone = phone_digits(self.cleaned_data["phone"])
        if not 8 <= len(phone) <= 15:
            raise forms.ValidationError(t("err_phone"))
        return phone

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()
