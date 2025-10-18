import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command

from server.settings.components.common import (
    AUTHORIZED_APPS,
    REGULAR_ADMIN_GROUP_NAME,
)

pytestmark = pytest.mark.django_db


def test_setup_regular_admin_prints_assigned_users(capfd):
    """Test: stampa finale 'Assigned users:' quando utenti vengono assegnati."""
    user_model = get_user_model()
    email = 'printuser@aslcn1.it'
    user_model.objects.create_user(email=email)
    call_command(
        'setup_regular_admin',
        '--apps',
        *AUTHORIZED_APPS,
        '--assign-users',
        email,
    )
    out, _ = capfd.readouterr()
    assert 'Assigned users:' in out


def test_setup_regular_admin_app_not_found(capfd):
    """Test: gestisce app non esistente e mostra messaggio di errore."""
    call_command('setup_regular_admin', '--apps', 'nonexistentapp')
    out, _ = capfd.readouterr()
    assert 'Skipping unknown apps' in out


def test_setup_regular_admin_user_not_found(capfd):
    """Test: gestisce utente non trovato e mostra messaggio di errore."""
    call_command(
        'setup_regular_admin',
        '--apps',
        *AUTHORIZED_APPS,
        '--assign-users',
        'missing@aslcn1.it',
    )
    out, _ = capfd.readouterr()
    assert 'User not found:' in out


def test_setup_regular_admin_dry_run_with_valid_input(capfd):
    """Test: dry-run con app e utente validi mostra azioni ma non applica."""
    user_model = get_user_model()
    email = 'dryrunvalid@aslcn1.it'
    user_model.objects.create_user(email=email)
    call_command(
        'setup_regular_admin',
        '--apps',
        *AUTHORIZED_APPS,
        '--assign-users',
        email,
        '--dry-run',
    )
    out, _ = capfd.readouterr()
    assert 'Would assign users:' in out
    assert not Group.objects.filter(name=REGULAR_ADMIN_GROUP_NAME).exists()


def test_setup_regular_admin_group_already_exists():
    """Test: il gruppo già esistente viene aggiornato senza errori."""
    user_model = get_user_model()
    email = 'already@aslcn1.it'
    user = user_model.objects.create_user(email=email)
    Group.objects.create(name=REGULAR_ADMIN_GROUP_NAME)
    call_command(
        'setup_regular_admin',
        '--apps',
        *AUTHORIZED_APPS,
        '--assign-users',
        email,
    )
    group = Group.objects.get(name=REGULAR_ADMIN_GROUP_NAME)
    assert user in group.user_set.all()


def test_setup_regular_admin_creates_group_and_assigns_user():
    """Test: crea gruppo e assegna utente, verifica permessi CRUD."""
    user_model = get_user_model()
    email = 'testuser@aslcn1.it'
    user = user_model.objects.create_user(email=email)
    assert not Group.objects.filter(name=REGULAR_ADMIN_GROUP_NAME).exists()
    call_command(
        'setup_regular_admin',
        '--apps',
        *AUTHORIZED_APPS,
        '--assign-users',
        email,
    )
    group = Group.objects.get(name=REGULAR_ADMIN_GROUP_NAME)
    assert user in group.user_set.all()
    perms = group.permissions.all()
    assert perms.count() > 0


def test_setup_regular_admin_dry_run_does_not_create():
    """Test: dry-run non crea gruppo né assegna utenti."""
    user_model = get_user_model()
    email = 'dryrun@aslcn1.it'
    user_model.objects.create_user(email=email)
    call_command(
        'setup_regular_admin',
        '--apps',
        *AUTHORIZED_APPS,
        '--assign-users',
        email,
        '--dry-run',
    )
    assert not Group.objects.filter(name=REGULAR_ADMIN_GROUP_NAME).exists()


def test_setup_regular_admin_handles_no_users():
    """Test: nessun utente assegnato al gruppo se non specificato."""
    call_command('setup_regular_admin', '--apps', *AUTHORIZED_APPS)
    group = Group.objects.get(name=REGULAR_ADMIN_GROUP_NAME)
    assert group.user_set.count() == 0


def test_setup_regular_admin_handles_no_apps():
    """Test: il gruppo non viene creato se nessuna app è specificata."""
    user_model = get_user_model()
    email = 'noapps@aslcn1.it'
    user_model.objects.create_user(email=email)
    call_command('setup_regular_admin', '--apps', '', '--assign-users', email)
    assert not Group.objects.filter(name=REGULAR_ADMIN_GROUP_NAME).exists()


def test_setup_regular_admin_idempotent():
    """Test idempotenza assegnazioni e permessi.

    Chiamate ripetute non creano duplicati e mantengono permessi/utenti.
    """
    user_model = get_user_model()
    email = 'idempotent@aslcn1.it'
    user = user_model.objects.create_user(email=email)
    call_command(
        'setup_regular_admin',
        '--apps',
        *AUTHORIZED_APPS,
        '--assign-users',
        email,
    )
    call_command(
        'setup_regular_admin',
        '--apps',
        *AUTHORIZED_APPS,
        '--assign-users',
        email,
    )
    group = Group.objects.get(name=REGULAR_ADMIN_GROUP_NAME)
    assert user in group.user_set.all()
    assert group.permissions.count() > 0
