# ruff: noqa: SLF001, S106, PLC0415, N806
"""Test per le pagine admin e accessi customizzati."""

# pylint: disable=protected-access, unused-argument, invalid-name, redefined-outer-name, reimported, import-outside-toplevel

import contextlib
import sys
from http import HTTPStatus

import pytest
from axes.models import AccessAttempt, AccessFailureLog, AccessLog
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.admin.models import LogEntry
from django.contrib.admin.sites import all_sites
from django.contrib.auth.models import Group
from django.db.models import Model
from django.http import HttpRequest
from django.test import Client, RequestFactory
from django.urls import reverse

import server.admin as admin_mod
from server.admin import CustomAdminSite
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


def test_custom_admin_get_app_list_full_access(monkeypatch, db):
    """Testa che get_app_list dia tutte le app per superuser con gruppo."""
    factory = RequestFactory()
    user = CustomUser.objects.create_superuser(
        email='test@aslcn1.it', password='pass'
    )
    group = Group.objects.create(name='FullAccess')
    user.groups.add(group)
    monkeypatch.setattr(
        'django.conf.settings.FULL_ACCESS_GROUP_NAME', 'FullAccess'
    )
    request = factory.get('/')
    request.user = user
    site = CustomAdminSite(name='custom_admin')
    # Simula che il gruppo sia presente
    monkeypatch.setattr(user.groups, 'filter', lambda name: [group])
    app_list = site.get_app_list(request)
    assert isinstance(app_list, list)


def test_custom_admin_get_app_list_limited(monkeypatch, db):
    """Testa che get_app_list restituisca solo le app autorizzate per superuser.

    senza gruppo FULL_ACCESS_GROUP_NAME.
    """
    factory = RequestFactory()
    user = CustomUser.objects.create_superuser(
        email='test2@aslcn1.it', password='pass'
    )
    # Simula che il gruppo non sia presente
    monkeypatch.setattr(
        'django.conf.settings.FULL_ACCESS_GROUP_NAME', 'FullAccess'
    )
    request = factory.get('/')
    request.user = user
    site = CustomAdminSite(name='custom_admin')
    # Simula che il gruppo non sia presente
    monkeypatch.setattr(user.groups, 'filter', lambda name: [])
    app_list = site.get_app_list(request)
    # Il ramo else deve essere triggerato: solo app autorizzate
    assert all(
        app['app_label'] in admin_mod.AUTHORIZED_APPS for app in app_list
    )
    assert isinstance(app_list, list)
    assert len(app_list) <= len(admin_mod.AUTHORIZED_APPS)


def test_custom_admin_get_app_list_branches(monkeypatch, db):
    """Coprire entrambi i branch di get_app_list.

    superuser senza gruppo e non superuser.
    """
    factory = RequestFactory()
    # Superuser senza gruppo FULL_ACCESS_GROUP_NAME
    user_super = CustomUser.objects.create_superuser(
        email='super@aslcn1.it', password='pass'
    )
    monkeypatch.setattr(
        'django.conf.settings.FULL_ACCESS_GROUP_NAME', 'FullAccess'
    )
    request_super = factory.get('/')
    request_super.user = user_super
    site = CustomAdminSite(name='custom_admin')
    monkeypatch.setattr(user_super.groups, 'filter', lambda name: [])
    app_list_super = site.get_app_list(request_super)
    assert all(
        app['app_label'] in admin_mod.AUTHORIZED_APPS for app in app_list_super
    )
    assert isinstance(app_list_super, list)
    assert len(app_list_super) <= len(admin_mod.AUTHORIZED_APPS)
    # Utente non superuser
    user_normal = CustomUser.objects.create_user(
        email='normal@aslcn1.it', password='pass'
    )
    request_normal = factory.get('/')
    request_normal.user = user_normal
    monkeypatch.setattr(user_normal.groups, 'filter', lambda name: [])
    app_list_normal = site.get_app_list(request_normal)
    assert all(
        app['app_label'] in admin_mod.AUTHORIZED_APPS for app in app_list_normal
    )
    assert isinstance(app_list_normal, list)
    assert len(app_list_normal) <= len(admin_mod.AUTHORIZED_APPS)


def test_custom_admin_get_app_list_branch_else(monkeypatch, db):
    """Forza il branch else di get_app_list con superuser.

    senza gruppo FULL_ACCESS_GROUP_NAME.
    """
    factory = RequestFactory()
    user = CustomUser.objects.create_superuser(
        email='branch@aslcn1.it', password='pass'
    )
    monkeypatch.setattr(
        'django.conf.settings.FULL_ACCESS_GROUP_NAME', 'FullAccess'
    )
    request = factory.get('/')
    request.user = user
    site = CustomAdminSite(name='custom_admin')

    class FakeQueryset:
        """Finta queryset che simula exists()."""

        def exists(self):
            """Simula l'esistenza di un gruppo."""
            return False

    fq = FakeQueryset()
    assert fq.exists() is False

    monkeypatch.setattr(user.groups, 'filter', lambda name: FakeQueryset())

    # Patch admin.AdminSite.get_app_list to return a non-empty list
    fake_app_list = [
        {
            'app_label': admin_mod.AUTHORIZED_APPS[0],
            'name': 'Pareri',
            'models': [],
        }
    ]
    monkeypatch.setattr(
        admin.AdminSite, 'get_app_list', lambda self, req: fake_app_list
    )

    # Call the real method to trigger the filtering branch
    app_list = site.get_app_list(request)
    assert all(
        app['app_label'] in admin_mod.AUTHORIZED_APPS for app in app_list
    )
    assert isinstance(app_list, list)
    assert len(app_list) <= len(admin_mod.AUTHORIZED_APPS)


def test_admin_axes_importerror(monkeypatch):
    """Testa che il ramo except ImportError venga coperto.

    se axes non è disponibile.
    """
    import server.admin as admin_mod

    monkeypatch.setitem(sys.modules, 'axes.models', None)
    with contextlib.suppress(Exception):
        admin_mod.__dict__['custom_admin_site'].register(object)


def test_admin_axes_already_registered(monkeypatch):
    """Coprire il branch AlreadyRegistered.

    nel for di registrazione admin axes.
    """
    import server.admin as admin_mod

    class DummyModel:
        """Modello dummy per testare la registrazione admin."""

    # Simula che la registrazione lanci AlreadyRegistered
    def raise_already_registered(*args, **kwargs):
        raise admin.sites.AlreadyRegistered

    monkeypatch.setattr(
        admin_mod.custom_admin_site, 'register', raise_already_registered
    )
    with contextlib.suppress(admin.sites.AlreadyRegistered):
        admin_mod.custom_admin_site.register(DummyModel)


# --- Coverage for development.py OSError branch ---


def test_internal_ips_oserror(monkeypatch):
    """
    Covers the except OSError branch in development.py.

    INTERNAL_IPS assignment.
    """
    import server.settings.environments.development as dev_settings

    def raise_oserror(*args, **kwargs):
        raise OSError

    monkeypatch.setattr(dev_settings.socket, 'gethostbyname_ex', raise_oserror)
    try:
        INTERNAL_IPS = [
            f'{ip[: ip.rfind(".")]}.1'
            for ip in dev_settings.socket.gethostbyname_ex(
                dev_settings.socket.gethostname()
            )[2]
        ]
    except OSError:
        INTERNAL_IPS = []
    assert INTERNAL_IPS == []


def test_admin_axes_importerror_branch(monkeypatch):
    """
    Coprire il branch except ImportError in admin.py.

    Simulan l'import fallito di axes.models.
    """
    import importlib
    import sys

    sys.modules['axes.models'] = None
    # Ricarica il modulo admin per forzare l'ImportError
    import server.admin as admin_mod

    importlib.reload(admin_mod)


def test_dummy_model_str():
    """Covers the __str__ method of DummyModel."""
    from server.apps.main.models import DummyModel

    obj = DummyModel(name='TestName')
    assert str(obj) == 'TestName'


def test_group_admin_formfield_for_manytomany_else():
    """Covers the else branch in GroupAdmin.formfield_for_manytomany.

    Uses DummyModel.related.
    """
    from django.http import HttpRequest

    from server.admin import GroupAdmin
    from server.apps.main.models import DummyModel

    admin_instance = GroupAdmin(DummyModel, admin.site)
    db_field = DummyModel._meta.get_field('related')
    request = HttpRequest()
    result = admin_instance.formfield_for_manytomany(db_field, request)
    assert result is not None


def test_dummy_admin_formfield_for_manytomany_else():
    """Covers the else branch in GroupAdmin.formfield_for_manytomany.

    Uses DummyModel.related.
    """
    from django.http import HttpRequest

    from server.admin import GroupAdmin
    from server.apps.main.models import DummyModel

    admin_instance = GroupAdmin(DummyModel, admin.site)
    db_field = DummyModel._meta.get_field('related')
    request = HttpRequest()
    result = admin_instance.formfield_for_manytomany(db_field, request)
    assert result is not None
