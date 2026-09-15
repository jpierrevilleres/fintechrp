from django import forms
from .models import ContactMessage, Newsletter, Comment

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


class CommentForm(forms.ModelForm):
    # Honeypot: invisible to real visitors, but bots that blindly fill
    # every field in a form tend to fill this one too. Not a model
    # field - just used to flag spam via is_spam() below.
    website = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'autocomplete': 'off',
        'tabindex': '-1',
    }))

    class Meta:
        model = Comment
        fields = ["name", "email", "body"]
        widgets = {
            'body': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your comment here…'}),
        }

    def is_spam(self):
        return bool(self.cleaned_data.get('website'))
