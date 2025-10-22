"""Test di base per admin datoriLavoro."""

import pytest
from django.contrib.admin.sites import AdminSite

from server.apps.datoriLavoro.admin import SedeAdmin
from server.apps.datoriLavoro.models import Sede


@pytest.mark.django_db
class TestSedeAdmin:
    """Test suite per l'admin di Sede."""

    def test_sede_admin_has_search_fields(self):
        """Verifica che search_fields sia configurato."""
        site = AdminSite()
        admin = SedeAdmin(Sede, site)

        assert hasattr(admin, 'search_fields')
        assert len(admin.search_fields) > 0
