from django import forms
from django.contrib.admin.forms import AdminAuthenticationForm
from django_otp.admin import OTPAdminSite
from django_otp.forms import OTPAuthenticationFormMixin
from django_otp.plugins.otp_static.models import StaticDevice
from django_otp.plugins.otp_totp.models import TOTPDevice


class CodeAuthenticationForm(OTPAuthenticationFormMixin, AdminAuthenticationForm):
    """Admin login form: username, password and one code, with no device picker."""

    otp_error_messages = dict(
        OTPAuthenticationFormMixin.otp_error_messages,
        invalid_token='Incorrect authentication code. Please try again.',
    )

    otp_token = forms.CharField(
        label='Authentication code',
        help_text='The 6-digit code from your authenticator app, or a backup code.',
        widget=forms.TextInput(attrs={'autocomplete': 'one-time-code'}),
    )

    def clean(self):
        cleaned_data = super().clean()
        user = self.get_user()
        token = ''.join(cleaned_data.get('otp_token', '').split()).lower()
        if user is not None and token:
            # Choose the device from the code's shape instead of trying each
            # one: every non-matching device would count a failed attempt and
            # end up throttled (e.g. the backup codes after each app login).
            model = TOTPDevice if token.isdigit() and len(token) == 6 else StaticDevice
            device = model.objects.filter(user=user, confirmed=True).first()
            if device is None:
                raise forms.ValidationError(self.otp_error_messages['invalid_token'], code='invalid_token')
            user.otp_device = self._verify_token(user, token, device)
        return cleaned_data


class CodeAdminSite(OTPAdminSite):
    login_form = CodeAuthenticationForm
    login_template = 'admin/otp_login.html'
