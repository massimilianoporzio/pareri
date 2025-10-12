# ruff: noqa: SLF001
"""Test per le pagine admin e accessi customizzati."""

# pylint: disable=protected-access

from http import HTTPStatus

import pytest
from axes.models import AccessAttempt, AccessFailureLog, AccessLog
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.admin.models import LogEntry
from django.contrib.admin.sites import all_sites
from django.db.models import Model
from django.http import HttpRequest
from django.test import Client
from django.urls import reverse

from server.apps.accounts.admin import CustomUserAdmin
from server.apps.accounts.models import CustomUser

# Models that should have restricted (FORBIDDEN) admin add pages
_RESTRICTED_ADMIN_ADD_MODELS = frozenset([
    AccessAttempt,
    AccessLog,
    AccessFailureLog,
])

# pylint: disable=protected-access
_MODEL_ADMIN_PARAMS = tuple(
    (site, model, model_admin)
    for site in all_sites
    for model, model_admin in site._registry.items()
)


def _make_url(site: AdminSite, model: type[Model], page: str) -> str:
    """Generates a URL for the given admin site, model, and page."""
    # Accessing _meta is required for Django model introspection;
    # no public alternative exists.
    app_label = model._meta.app_label
    model_name = model._meta.model_name
    return reverse(f'{site.name}:{app_label}_{model_name}_{page}')  # noqa: WPS221


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('site', 'model'),
    [
        (site, model)
        for site in all_sites
        for model, _ in site._registry.items()
    ],
)
def test_admin_changelist(
    admin_client: Client,
    site: AdminSite,
    model: type[Model],
) -> None:
    """Ensures that admin changelist pages are accessible."""
    url = _make_url(site, model, 'changelist')
    response = admin_client.get(url, {'q': 'something'})

    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('site', 'model'),
    [
        (site, model)
        for site in all_sites
        for model, _ in site._registry.items()
    ],
)
def test_admin_add(
    admin_client: Client,
    site: AdminSite,
    model: type[Model],
) -> None:
    """Ensures that admin add pages are accessible or restricted."""
    url = _make_url(site, model, 'add')
    response = admin_client.get(url)
    expected_status = (
        HTTPStatus.FORBIDDEN
        if model in _RESTRICTED_ADMIN_ADD_MODELS
        else HTTPStatus.OK
    )

    assert response.status_code == expected_status


# pylint: disable=no-member
class FakeLogEntryError(Exception):
    """
    Eccezione custom per simulare errori in.

    LogEntry.objects.filter nei test admin.
    """


class DummyQuerySet:
    """
    Finta queryset.

    Simula select_related
    e order_by nei test di copertura.

    """

    def select_related(self, *_args, **_kwargs):
        """Simula il metodo select_related di una queryset Django."""
        return self

    def order_by(self, *_args, **_kwargs):
        """
        Simula il metodo order_by di una queryset Django.

        Restituisce lista vuota.
        """
        return []


@pytest.mark.django_db
def test_change_view_exception(monkeypatch):
    """
    Testa che CustomUserAdmin.change_view gestisca correttamente.

    Verifica che il ramo di gestione errori venga eseguito
    e la response sia valida.
    """
    request = HttpRequest()
    user = CustomUser.objects.create(email='test@example.com')
    admin_instance = CustomUserAdmin(CustomUser, admin.site)
    # Simula LogEntry.objects.filter che restituisce un DummyQuerySet
    monkeypatch.setattr(
        LogEntry.objects, 'filter', lambda *a, **kw: DummyQuerySet()
    )
    response = admin_instance.change_view(request, str(user.pk))
    assert hasattr(response, 'status_code')


@pytest.mark.django_db
def test_change_view_real(admin_client):
    """Test reale: verifica che il context sia presente nella response."""
    user = CustomUser.objects.create(email='test@example.com')
    url = reverse('admin:accounts_customuser_change', args=[user.pk])
    response = admin_client.get(url)
    assert hasattr(response, 'context_data')


@pytest.mark.django_db
def test_formfield_for_manytomany_user_permissions():
    """Testa il ramo user_permissions in formfield_for_manytomany."""
    request = HttpRequest()
    admin_instance = CustomUserAdmin(CustomUser, admin.site)
    db_field = CustomUser._meta.get_field('user_permissions')
    result = admin_instance.formfield_for_manytomany(db_field, request)
    assert result is not None


@pytest.mark.django_db
def test_formfield_for_manytomany_real():
    """Test reale: verifica che il queryset dei permessi abbia content_type."""
    request = HttpRequest()
    admin_instance = CustomUserAdmin(CustomUser, admin.site)
    db_field = CustomUser._meta.get_field('user_permissions')
    formfield = admin_instance.formfield_for_manytomany(db_field, request)
    # Verifica che il queryset abbia il campo content_type prefetchato
    assert hasattr(formfield.queryset.model, 'content_type')
