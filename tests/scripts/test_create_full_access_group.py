"""Test per lo script create_full_access_group.py."""

import pytest
from django.contrib.auth.models import Group

import scripts.create_full_access_group as script


@pytest.mark.django_db
def test_main_group_already_exists(monkeypatch, settings):
    """Verifica il ramo in cui il gruppo esiste già."""
    settings.FULL_ACCESS_GROUP_NAME = 'Test Full Access Exists'
    Group.objects.get_or_create(name=settings.FULL_ACCESS_GROUP_NAME)
    output = []
    monkeypatch.setattr('builtins.print', output.append)
    script.main()
    assert any('esiste già' in msg for msg in output)


@pytest.mark.django_db
def test_main_creates_group(monkeypatch, settings):
    """Verifica che il gruppo venga creato."""
    settings.FULL_ACCESS_GROUP_NAME = 'Test Full Access Create'
    Group.objects.filter(name=settings.FULL_ACCESS_GROUP_NAME).delete()
    output = []
    monkeypatch.setattr('builtins.print', output.append)
    script.main()
    assert Group.objects.filter(name=settings.FULL_ACCESS_GROUP_NAME).exists()
    assert any('Creato gruppo' in msg for msg in output)
