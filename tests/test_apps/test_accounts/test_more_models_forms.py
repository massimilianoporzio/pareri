"""Tests for additional models and forms in accounts app."""

import pytest
from django.core.exceptions import ValidationError

from server.apps.accounts.forms import CustomUserCreationForm
from server.apps.accounts.models import CustomUser, CustomUserManager

pytestmark = pytest.mark.django_db


def test_email_prefix_display_property():
    """email_prefix_display returns part before @ or empty string."""
    u = CustomUser(email='pippo@aslcn1.it')
    assert u.email_prefix_display == 'pippo'
    u.email = ''
    assert not u.email_prefix_display


def test_manager_full_clean_rejects_wrong_domain():
    """CustomUserManager.full_clean should raise on non-aslcn1.it domain."""
    m = CustomUserManager()
    with pytest.raises(ValidationError):
        m.full_clean('bad@not-company.com')


def test_clean_method_on_model_rejects_wrong_domain():
    """Model.clean should raise ValidationError for wrong email domain."""
    u = CustomUser(email='x@y.com')
    with pytest.raises(ValidationError):
        u.clean()


def test_creation_form_password_mismatch():
    """Form invalid when password and password2 do not match."""
    data = {
        'email': 'a@aslcn1.it',
        'password': 'one',
        'password2': 'two',
    }
    form = CustomUserCreationForm(data)
    # don't call form.is_valid() because ModelForm.unique checks hit the DB
    # set cleaned_data manually and call the validator to assert mismatch
    form.cleaned_data = {
        'password': data['password'],
        'password2': data['password2'],
    }
    with pytest.raises(ValidationError):
        form.clean_password2()
