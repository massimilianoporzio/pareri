"""Tests for accounts migrations."""

import pytest
from django_test_migrations.migrator import Migrator


def test_initial0001(migrator: Migrator) -> None:
    """Tests the initial migration forward application for accounts."""
    # The app label for accounts migrations
    app_label = 'accounts'
    old_state = migrator.apply_initial_migration((app_label, None))
    with pytest.raises(LookupError):
        old_state.apps.get_model(app_label, 'CustomUser')

    new_state = migrator.apply_tested_migration((app_label, '0001_initial'))
    model = new_state.apps.get_model(app_label, 'CustomUser')

    assert model.objects.create(email='migtest@aslcn1.it')
