"""Test per lo script create_full_access_group.py."""

import pytest
from django.contrib.auth.models import Group

import scripts.create_full_access_group as script

# pylint: disable=unnecessary-lambda


@pytest.mark.django_db
def test_main_creates_group(monkeypatch, settings):
    """Verifica che il gruppo venga creato o esista già."""
    settings.FULL_ACCESS_GROUP_NAME = 'Test Full Access'
    # Rimuovi il gruppo se esiste
    Group.objects.filter(name=settings.FULL_ACCESS_GROUP_NAME).delete()
    output = []
    monkeypatch.setattr('builtins.print', lambda msg: output.append(msg))  # noqa: PLW0108
    script.main()
    assert Group.objects.filter(name=settings.FULL_ACCESS_GROUP_NAME).exists()
    assert any('Creato gruppo' in msg or 'esiste già' in msg for msg in output)
