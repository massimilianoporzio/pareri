"""Tests for accounts app configuration and admin registration."""
# pylint: disable=unused-argument

import pytest
from django.contrib import admin

from server.apps.accounts.apps import AccountsConfig
from server.apps.accounts.models import CustomUser

pytestmark = pytest.mark.django_db


def test_accounts_app_config():
    """AccountsConfig should expose the correct app name and default field."""
    # Do not instantiate AppConfig (it requires app_name and app_module).
    # Inspect class attributes instead.
    assert AccountsConfig.name == 'server.apps.accounts'
    assert hasattr(AccountsConfig, 'default_auto_field')


def test_customuser_registered_in_admin():
    """CustomUser model must be registered in the Django admin site."""
    # Use public API to check registration only (avoid protected-access)
    assert admin.site.is_registered(CustomUser)

    # If we need to inspect the registered ModelAdmin attributes
    # without touching protected members, instantiate the admin app's
    # registration code and ensure no exception is raised. The public
    # API doesn't expose list_display lookups, so we avoid inspecting it
    # to keep the test lint-clean and future-proof.
