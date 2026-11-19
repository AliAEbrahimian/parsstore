from django import forms

from .models import Customer, Inquiry
from .utils import phone_digits

INPUT_CLASS = "field-input"


class HoneypotMixin(forms.Form):
    """فیلد تلهٔ مشترک فرم‌ها؛ کاربر واقعی آن را نمی‌بیند."""

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
        """اگر این فیلد پنهان پر شده باشد، درخواست ربات است."""
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("درخواست نامعتبر است.")
        return ""


class InquiryForm(HoneypotMixin, forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ["name", "company", "phone", "email", "machine", "message"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "مثلاً: علی رضایی",
                    "autocomplete": "name",
                    "maxlength": 120,
                }
            ),
            "company": forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "مثلاً: نساجی البرز",
                    "autocomplete": "organization",
                    "maxlength": 160,
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "۰۹۱۲ ۰۰۰ ۰۰۰۰",
                    "inputmode": "tel",
                    "autocomplete": "tel",
                    "dir": "ltr",
                    "maxlength": 30,
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "name@example.com",
                    "inputmode": "email",
                    "autocomplete": "email",
                    "dir": "ltr",
                    "maxlength": 254,
                }
            ),
            "machine": forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "مثلاً: Picanol GTX",
                    "autocomplete": "off",
                    "maxlength": 120,
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "class": INPUT_CLASS,
                    "rows": 4,
                    "maxlength": 2000,
                    "placeholder": "فهرست قطعات یا شماره فنی قطعه مورد نیاز را بنویسید…",
                }
            ),
        }

    def clean_name(self):
        return " ".join(self.cleaned_data["name"].split())

    def clean_company(self):
        return " ".join(self.cleaned_data.get("company", "").split())

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        digits = phone_digits(phone)
        if len(digits) < 8:
            raise forms.ValidationError("شماره تماس معتبر وارد کنید.")
        return phone

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()

    def clean_message(self):
        message = self.cleaned_data["message"].strip()
        if len(message) < 5:
            raise forms.ValidationError("توضیحات را کامل‌تر بنویسید.")
        if len(message) > 2000:
            raise forms.ValidationError("توضیحات حداکثر ۲۰۰۰ نویسه می‌تواند باشد.")
        return message


class ClubSignupForm(HoneypotMixin, forms.ModelForm):
    """درخواست عضویت در باشگاه مشتریان؛ پس از تأیید مدیر فعال می‌شود."""

    class Meta:
        model = Customer
        fields = ["first_name", "last_name", "company", "phone", "email"]
        labels = {
            "first_name": "نام",
            "last_name": "نام خانوادگی",
            "company": "شرکت / کارگاه",
            "phone": "شماره تماس",
            "email": "آدرس ایمیل",
        }
        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "مثلاً: مریم",
                    "autocomplete": "given-name",
                    "maxlength": 60,
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "مثلاً: احمدی",
                    "autocomplete": "family-name",
                    "maxlength": 60,
                }
            ),
            "company": forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "مثلاً: نساجی البرز",
                    "autocomplete": "organization",
                    "maxlength": 160,
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "۰۹۱۲ ۰۰۰ ۰۰۰۰",
                    "inputmode": "tel",
                    "autocomplete": "tel",
                    "dir": "ltr",
                    "maxlength": 20,
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "name@example.com",
                    "inputmode": "email",
                    "autocomplete": "email",
                    "dir": "ltr",
                    "maxlength": 254,
                }
            ),
        }

    def clean_first_name(self):
        return " ".join(self.cleaned_data["first_name"].split())

    def clean_last_name(self):
        return " ".join(self.cleaned_data["last_name"].split())

    def clean_company(self):
        return " ".join(self.cleaned_data.get("company", "").split())

    def clean_phone(self):
        phone = phone_digits(self.cleaned_data["phone"])
        if not 8 <= len(phone) <= 15:
            raise forms.ValidationError("شماره تماس معتبر وارد کنید.")
        return phone

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()
