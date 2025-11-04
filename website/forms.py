from django import forms
from .models import ContactMessage, Newsletter

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "message"]

class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ["email"]
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email'})
        }
