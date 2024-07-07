from django import forms
from django.forms.models import inlineformset_factory
from .models import Course, Module, Payment
from django.contrib.auth.models import User

Moduleformset = inlineformset_factory(
    Course, Module, fields=["title", "description"], extra=2, can_delete=True
)


class Admission_form(forms.Form):
    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    course = forms.ModelMultipleChoiceField(queryset=Course.objects.all())
    certificate_issued = forms.BooleanField(required=False)
    enrollment_date = forms.DateField(required=True)


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["amount"]

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True, label="Your Name")
    email = forms.EmailField(required=True, label="Your Email")
    subject = forms.CharField(max_length=200, required=True, label="Subject")
    message = forms.CharField(widget=forms.Textarea, required=True, label="Message")
