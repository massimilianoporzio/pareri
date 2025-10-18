"""Test per i form datoriLavoro."""

from unittest.mock import patch

import pytest

from server.apps.datoriLavoro.forms import DatoreLavoroForm


@pytest.mark.django_db
class TestDatoreLavoroForm:
    """Test per DatoreLavoroForm."""

    def test_form_clean_requires_at_least_one_field(self):
        """Test che clean() richieda almeno un campo identificativo."""
        form = DatoreLavoroForm(data={})
        assert not form.is_valid()
        errors_str = str(form.errors)
        assert 'almeno uno' in errors_str.lower()

    def test_form_valid_with_ragione_sociale(self):
        """Test che il form sia valido con ragione sociale."""
        form = DatoreLavoroForm(
            data={
                'ragione_sociale': 'Test Company',
            }
        )
        assert form.is_valid(), form.errors

    @patch('server.apps.datoriLavoro.models.get_from_eu_vies', autospec=True)
    def test_form_valid_with_p_iva(self, mock_vies):
        """Test che il form sia valido con P.IVA."""
        mock_vies.return_value = {'valid': True}
        form = DatoreLavoroForm(
            data={
                'p_iva': '12345678901',
            }
        )
        assert form.is_valid(), form.errors

    def test_form_valid_with_codice_fiscale(self):
        """Test che il form sia valido con codice fiscale."""
        form = DatoreLavoroForm(
            data={
                'codice_fiscale': 'RSSMRA80A01H501U',
            }
        )
        assert form.is_valid(), form.errors
