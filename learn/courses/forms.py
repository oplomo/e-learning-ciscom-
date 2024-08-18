from django import forms
from django.forms.models import inlineformset_factory, modelformset_factory
from .models import Course, Module, Payment, Enrollment, Perfomance
from account.models import CustomUser
from django.contrib.auth.models import User
from django.forms import BaseFormSet, formset_factory
from django.forms import BaseModelFormSet, modelformset_factory


Moduleformset = inlineformset_factory(
    Course, Module, fields=["title", "description"], extra=2, can_delete=True
)


class Admission_form(forms.Form):
    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField(required=False)
    course = forms.ModelMultipleChoiceField(queryset=Course.objects.all())
    certificate_issued = forms.BooleanField(required=False)
    enrollment_date = forms.DateField(required=True)
    finishing_date = forms.DateField(required=False)


class PaymentForm(forms.ModelForm):
    payment_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))

    class Meta:
        model = Payment
        fields = ["amount", "payment_date"]

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


class CourseSelectForm(forms.Form):
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(), label="Course", required=True
    )

