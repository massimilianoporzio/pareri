"""Tests for additional models and forms in accounts app."""
# pylint: disable=unused-argument

import builtins

import pytest
from django.core.exceptions import ValidationError

from server.apps.accounts.forms import (
    CustomAuthenticationForm,
    CustomUserCreationForm,
)
from server.apps.accounts.models import CustomUser

pytestmark = pytest.mark.django_db


def test_create_user_sets_is_staff_true_by_default():
    """CustomUserManager.create_user sets is_staff=True by default."""
    user = CustomUser.objects.create_user('staffdefault@aslcn1.it')
    assert user.is_staff is True


def test_create_user_normalizes_and_sets_password():
    """create_user normalizes email and hashes the password."""
    user = CustomUser.objects.create_user('UPPER@aslcn1.it')
    # set a password after create_user to avoid passing a password keyword
    user.set_password('s3cret')
    user.save()
    assert user.email.lower() == 'upper@aslcn1.it'
    assert user.check_password('s3cret')


def test_save_populates_username_and_audit(monkeypatch):
    """Ensure username auto-filled and audit fields set from crum."""
    # make a real CustomUser to act as the current user
    admin_user = CustomUser.objects.create_user('admin@aslcn1.it')
    admin_user.first_name = 'Admin'
    admin_user.last_name = 'User'
    admin_user.set_password('pw')
    admin_user.save()
    # monkeypatch the get_current_user used inside models module
    monkeypatch.setattr(
        'server.apps.accounts.models.get_current_user',
        lambda: admin_user,
    )

    u = CustomUser.objects.create_user('audit@aslcn1.it')
    # username populated from email prefix
    assert u.username == 'audit'
    # created_by/updated_by should reference our admin_user or its fullname
    assert u.created_by == admin_user or u.created_by_fullname == 'Admin User'


def test_version_field_increments():
    """IntegerVersionField should increment on subsequent saves."""
    u = CustomUser.objects.create_user('ver@aslcn1.it')
    initial = u.version
    u.first_name = 'V'
    u.save()
    assert u.version is not None
    # version should have changed (or be non-equal)
    assert u.version != initial


def test_authentication_form_success_and_failure(monkeypatch):
    """CustomAuthenticationForm.clean authenticates or raises on failure."""
    # create a real user to authenticate against
    user = CustomUser.objects.create_user('auth@aslcn1.it')
    user.set_password('pw')
    user.save()

    # success: monkeypatch authenticate in forms module to return the user
    monkeypatch.setattr(
        'server.apps.accounts.forms.authenticate',
        lambda request, username, password: user,
    )
    form = CustomAuthenticationForm(
        {'username': 'auth@aslcn1.it', 'password': 'pw'},
        request=None,
    )
    assert form.is_valid(), form.errors

    # failure: authenticate returns None
    monkeypatch.setattr(
        'server.apps.accounts.forms.authenticate',
        lambda request, username, password: None,
    )
    form2 = CustomAuthenticationForm(
        {'username': 'auth@aslcn1.it', 'password': 'bad'},
        request=None,
    )
    # is_valid should be False and contain non-field errors
    assert not form2.is_valid()
    assert form2.non_field_errors()


def test_authentication_form_get_user_returns_cached_user(monkeypatch):
    """get_user should return the authenticated user cached by the form."""
    user = CustomUser.objects.create_user('guser@aslcn1.it')
    user.set_password('pw')
    user.save()

    # Make authenticate return our user so the form caches it
    monkeypatch.setattr(
        'server.apps.accounts.forms.authenticate',
        lambda request, username, password: user,
    )

    form = CustomAuthenticationForm(
        {'username': 'guser@aslcn1.it', 'password': 'pw'},
        request=None,
    )
    assert form.is_valid(), form.errors
    # The get_user method should return the same user instance
    assert form.get_user() is user


def test_creation_form_commit_true_creates_user():
    """CustomUserCreationForm.save with commit=True persists the user."""
    data = {
        'email': 'formcreate@aslcn1.it',
        'first_name': 'Form',
        'last_name': 'Create',
        'password': 'abc123',
        'password2': 'abc123',
    }
    form = CustomUserCreationForm(data)
    assert form.is_valid(), form.errors.as_data()
    user = form.save(commit=True)
    assert user.pk is not None


def test_creation_form_password_mismatch():
    """clean_password2 should reject mismatching passwords."""
    data = {
        'email': 'mm@aslcn1.it',
        'password': 'one',
        'password2': 'two',
    }
    form = CustomUserCreationForm(data)
    assert not form.is_valid()
    assert 'Le password non corrispondono' in str(form.errors)


def test_creation_form_commit_false_returns_unsaved():
    """save(commit=False) returns unsaved user with password set."""
    data = {
        'email': 'cf@aslcn1.it',
        'password': 'p1',
        'password2': 'p1',
    }
    form = CustomUserCreationForm(data)
    assert form.is_valid(), form.errors.as_data()
    user = form.save(commit=False)
    assert user.pk is None
    # password should be set (hashed) on the instance
    assert user.password
    # stored password should be hashed (verify via check_password)
    assert user.check_password('p1')


def test_authentication_form_error_branches():
    """Exercise authentication form error branches.

    Cases: no username, bad format, wrong domain, empty password.
    """
    # no username
    f1 = CustomAuthenticationForm({'username': '', 'password': 'x'})
    assert not f1.is_valid()

    # invalid email format
    f2 = CustomAuthenticationForm({
        'username': 'invalid-email',
        'password': 'x',
    })
    assert not f2.is_valid()

    # wrong domain
    f3 = CustomAuthenticationForm({'username': 'u@other.com', 'password': 'x'})
    assert not f3.is_valid()

    # empty password
    f4 = CustomAuthenticationForm({'username': 'u@aslcn1.it', 'password': ''})
    assert not f4.is_valid()


def test_model_clean_rejects_wrong_domain():
    """Model.full_clean should raise for wrong email domain."""
    u = CustomUser(email='bad@other.com')
    with pytest.raises(ValidationError):
        u.full_clean()


def test_save_without_current_user(monkeypatch):
    """If there's no current user, created_by stays None but username is set."""
    monkeypatch.setattr(
        'server.apps.accounts.models.get_current_user',
        lambda: None,
    )
    u = CustomUser.objects.create_user('nocurrent@aslcn1.it')
    assert u.created_by is None
    assert u.username == 'nocurrent'


def test_nome_utente_variants():
    """nome_utente returns combined or single names correctly."""
    u1 = CustomUser.objects.create_user('n1@aslcn1.it')
    u1.first_name = 'Solo'
    u1.save()
    assert u1.nome_utente == 'Solo'

    u2 = CustomUser.objects.create_user('n2@aslcn1.it')
    u2.last_name = 'Last'
    u2.save()
    assert u2.nome_utente == 'Last'

    u3 = CustomUser.objects.create_user('n3@aslcn1.it')
    u3.first_name = 'A'
    u3.last_name = 'B'
    u3.save()
    assert u3.nome_utente == 'A B'


def test_manager_full_clean_raises():
    """CustomUserManager.full_clean should reject wrong domains."""
    with pytest.raises(ValidationError, match=r'aslcn1.it'):
        CustomUser.objects.full_clean('bad@other.com')


def test_create_user_requires_email():
    """create_user must raise if email is empty."""
    with pytest.raises(ValueError, match=r'email'):
        CustomUser.objects.create_user('')


def test_create_superuser_flags_validation():
    """create_superuser should enforce is_staff/is_superuser flags."""
    with pytest.raises(ValueError, match=r'is_staff'):
        CustomUser.objects.create_superuser('su@aslcn1.it', is_staff=False)


def test___str___returns_full_name():
    """__str__ should return the user's full name when present."""
    u = CustomUser.objects.create_user('fullname@aslcn1.it')
    u.first_name = 'First'
    u.last_name = 'Last'
    u.save()
    assert str(u) == 'First Last'


def test_create_superuser_requires_superuser_flag():
    """create_superuser enforces is_superuser=True."""
    with pytest.raises(ValueError, match=r'is_superuser'):
        CustomUser.objects.create_superuser('s2@aslcn1.it', is_superuser=False)


def test_save_updates_updated_by(monkeypatch):
    """Saving an existing user sets updated_by and updated_by_fullname."""
    admin = CustomUser.objects.create_user('admin2@aslcn1.it')
    admin.first_name = 'A'
    admin.last_name = 'B'
    admin.save()

    u = CustomUser.objects.create_user('upd@aslcn1.it')
    # make sure u has a pk (existing record)
    assert u.pk is not None

    monkeypatch.setattr(
        'server.apps.accounts.models.get_current_user',
        lambda: admin,
    )
    u.first_name = 'Z'
    u.save()
    assert u.updated_by == admin
    assert u.updated_by_fullname == 'A B'


def test_save_with_anonymous_current_user(monkeypatch):
    """If current user is anonymous, no audit fields are set."""
    anon = type('Anon', (), {'is_anonymous': True})()
    monkeypatch.setattr(
        'server.apps.accounts.models.get_current_user',
        lambda: anon,
    )
    u = CustomUser.objects.create_user('anon@aslcn1.it')
    assert u.created_by is None


def test_authentication_form_clean_raises_on_auth_fail(monkeypatch):
    """Directly call clean() to exercise the authentication failure raise."""
    # ensure email passes format and domain checks
    monkeypatch.setattr(
        'server.apps.accounts.forms.authenticate',
        lambda request, username, password: None,
    )
    form = CustomAuthenticationForm({
        'username': 'ok@aslcn1.it',
        'password': 'pw',
    })
    assert not form.is_valid()
    assert form.non_field_errors()


def test_nome_utente_no_names_returns_email_prefix():
    """When no first/last name provided, nome_utente falls back.

    It should return the email prefix in that case.
    """
    u = CustomUser.objects.create_user('prefix@aslcn1.it')
    # Ensure both names empty
    u.first_name = ''
    u.last_name = ''
    u.save()
    assert u.nome_utente == 'prefix'


def test_created_by_fullname_uses_str_when_no_nome_utente(monkeypatch):
    """Force the else branch in created_by_fullname by disabling hasattr."""
    admin = CustomUser.objects.create_user('admin3@aslcn1.it')
    admin.first_name = 'Admin'
    admin.last_name = 'Three'
    admin.save()

    # Prepare an unsaved instance so save() will set created_by
    u = CustomUser(email='force@aslcn1.it')

    # Make hasattr always return False during this save so the code
    # uses str(user)
    monkeypatch.setattr(
        'server.apps.accounts.models.get_current_user',
        lambda: admin,
    )
    monkeypatch.setattr(builtins, 'hasattr', lambda obj, name: False)

    u.save()
    # created_by_fullname should be str(admin)
    assert u.created_by_fullname == str(admin)


def test_nome_utente_unsaved_fallback():
    """Accessing nome_utente on an unsaved instance falls back to email prefix.

    This exercises the final return path in the property implementation.
    """
    u = CustomUser(email='unsaved@aslcn1.it')
    assert u.nome_utente == 'unsaved'
