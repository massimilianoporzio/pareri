# pylint: disable=unused-argument
"""Pytest configuration and fixtures for the test suite.

This module provides global pytest plugins and reusable fixtures used
across the project's tests.
"""

import pytest

pytest_plugins = [
    # Should be the first custom one:
    'plugins.django_settings',
    'plugins.main.main_templates',
]


@pytest.fixture
def admin_user(django_user_model):
    """Create a superuser whose username/email matches project domain.

    This overrides the pytest-django default which might create a
    username without the required '@aslcn1.it' domain and so would
    trigger the project's email domain validation.
    """
    username_field = django_user_model.USERNAME_FIELD
    kwargs = {username_field: 'admin@aslcn1.it', 'password': 'pw'}
    return django_user_model.objects.create_superuser(**kwargs)
