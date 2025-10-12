"""Forms module for accounts app.

This module contains custom forms for user authentication and
management.
"""

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _

from .models import CustomUser


class CustomAuthenticationForm(forms.Form):
    """Custom authentication form for email-based login."""

    username = forms.CharField(max_length=254)
    password = forms.CharField(
        label=_('Password'), strip=False, widget=forms.PasswordInput
    )

    def __init__(self, *args, request=None, **kwargs):
        """Initialize form with request object.

        Args:
            request: The HTTP request object
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        """Validate form data and authenticate user.

        Returns:
            dict: The cleaned form data

        Raises:
            ValidationError: If validation or authentication fails
        """
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if not username:
            raise ValidationError(_("L'indirizzo email non può essere vuoto."))

        # PRIMO STEP: Validazione del formato e del dominio dell'email
        try:
            # Verifica il formato dell'email
            validate_email(username)
        except ValidationError as exc:
            raise ValidationError(
                _(
                    'Per favore, inserisci un indirizzo email'
                    ' valido come username.'
                )
            ) from exc

        # Verifica il dominio - Dominio aziendale richiesto
        if not username.endswith('@aslcn1.it'):
            raise ValidationError(
                _("Il dominio dell'indirizzo email deve essere '@aslcn1.it'.")
            )

        # SECONDO STEP: Autenticazione
        # (solo se la validazione del formato e del dominio passano)
        if password:
            self.user_cache = authenticate(
                self.request, username=username, password=password
            )
            if self.user_cache is None:
                raise ValidationError(
                    _(
                        'Inserisci un indirizzo email aziendale e password '
                        'corretti per un account di staff.'
                    )
                )
        else:
            raise ValidationError(_('La password non può essere vuota.'))

        return self.cleaned_data

    def get_user(self):
        """Get the authenticated user instance.

        Returns:
            CustomUser: The authenticated user or None
        """
        return self.user_cache


class CustomUserCreationForm(forms.ModelForm):
    """Form for creating new users with password confirmation."""

    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Ripeti password', widget=forms.PasswordInput
    )

    class Meta:
        """Meta configuration for the form."""

        model = CustomUser
        fields = (
            'email',
            'first_name',
            'last_name',
            'gender',
            'is_staff',
            'is_active',
            'groups',
        )

    def clean_password2(self):
        """Validate password confirmation.

        Returns:
            str: The confirmed password

        Raises:
            ValidationError: If passwords don't match
        """
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password and password2 and password != password2:
            raise forms.ValidationError('Le password non corrispondono.')
        return password2

    def save(self, commit: bool = True):  # noqa: FBT001,FBT002
        """Save the user with the given password.

        This overrides ``ModelForm.save`` and keeps the same signature so
        external callers can pass ``commit`` as expected.

        Args:
            commit: Whether to save to database immediately

        Returns:
            CustomUser: The created user instance
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class CustomUserChangeForm(forms.ModelForm):
    """Form for changing user details in admin."""

    password = ReadOnlyPasswordHashField(label='Password')

    class Meta:
        """Meta configuration for the form."""

        model = CustomUser
        fields = (
            'email',
            'first_name',
            'last_name',
            'gender',
            'is_staff',
            'is_active',
            'groups',
            'user_permissions',
        )
