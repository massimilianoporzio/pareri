"""Test per i modelli datoriLavoro."""

import pytest
from django.core.exceptions import ValidationError

from server.apps.datoriLavoro.models import (
    DatoreLavoro,
    DatoreLavoroSede,
    Sede,
    validate_codice_fiscale,
    validate_p_iva_italiana,
)


@pytest.fixture
def city():
    """Fixture per creare una città di test."""
    from server.apps.main.models import CityProxy

    city = CityProxy.objects.first()
    if not city:
        pytest.skip('Nessuna città disponibile nel database')
    return city


@pytest.mark.django_db
class TestSede:
    """Test per il modello Sede."""

    def test_sede_str(self, city):
        """Test metodo __str__ di Sede."""
        sede = Sede.objects.create(
            nome='Sede Principale',
            indirizzo='Via Roma 1',
            citta=city,
        )
        assert str(sede) == f'Sede Principale - {city}'

    def test_sede_str_without_nome(self, city):
        """Test metodo __str__ quando nome è vuoto."""
        sede = Sede.objects.create(
            nome='',
            citta=city,
        )
        assert 'Anonima' in str(sede)


@pytest.mark.django_db
class TestDatoreLavoro:
    """Test per il modello DatoreLavoro."""

    def test_datore_lavoro_str_with_ragione_sociale(self):
        """Test __str__ con ragione sociale."""
        datore = DatoreLavoro.objects.create(ragione_sociale='Acme Corporation')
        assert str(datore) == 'Acme Corporation'

    def test_datore_lavoro_str_with_p_iva(self):
        """Test __str__ con solo P.IVA."""
        datore = DatoreLavoro.objects.create(p_iva='12345678901')
        assert str(datore) == '12345678901'

    def test_datore_lavoro_str_with_codice_fiscale(self):
        """Test __str__ con solo codice fiscale."""
        datore = DatoreLavoro.objects.create(codice_fiscale='RSSMRA80A01H501U')
        assert str(datore) == 'RSSMRA80A01H501U'

    def test_datore_lavoro_clean_requires_at_least_one_field(self):
        """Test che clean() richieda almeno un campo."""
        datore = DatoreLavoro()
        with pytest.raises(ValidationError) as exc_info:
            datore.clean()
        assert 'almeno uno' in str(exc_info.value).lower()

    def test_datore_lavoro_clean_with_ragione_sociale(self):
        """Test clean() con ragione sociale."""
        datore = DatoreLavoro(ragione_sociale='Test Corp')
        datore.clean()  # Non deve sollevare eccezioni

    def test_datore_lavoro_save_uppercase_codice_fiscale(self):
        """Test che save() converta il codice fiscale in maiuscolo."""
        datore = DatoreLavoro.objects.create(codice_fiscale='rssmra80a01h501u')
        assert datore.codice_fiscale == 'RSSMRA80A01H501U'


@pytest.mark.django_db
class TestDatoreLavoroSede:
    """Test per il modello DatoreLavoroSede."""

    def test_datore_lavoro_sede_clean_prevents_duplicate_legal_office(
        self, city
    ):
        """Test che clean() impedisca duplicati di sede legale."""
        sede = Sede.objects.create(nome='Sede 1', citta=city)
        datore1 = DatoreLavoro.objects.create(ragione_sociale='Datore 1')
        datore2 = DatoreLavoro.objects.create(ragione_sociale='Datore 2')

        # Prima associazione come sede legale
        DatoreLavoroSede.objects.create(
            datore_lavoro=datore1,
            sede=sede,
            is_sede_legale=True,
        )

        # Tentativo di associare la stessa sede come legale per altro datore
        assoc2 = DatoreLavoroSede(
            datore_lavoro=datore2,
            sede=sede,
            is_sede_legale=True,
        )

        with pytest.raises(ValidationError) as exc_info:
            assoc2.clean()
        assert 'sede legale' in str(exc_info.value).lower()

    def test_datore_lavoro_sede_clean_allows_non_legal_duplicate(self, city):
        """Test che clean() permetta sedi non legali duplicate."""
        sede = Sede.objects.create(nome='Sede 1', citta=city)
        datore1 = DatoreLavoro.objects.create(ragione_sociale='Datore 1')
        datore2 = DatoreLavoro.objects.create(ragione_sociale='Datore 2')

        # Due associazioni NON legali alla stessa sede
        DatoreLavoroSede.objects.create(
            datore_lavoro=datore1,
            sede=sede,
            is_sede_legale=False,
        )

        assoc2 = DatoreLavoroSede(
            datore_lavoro=datore2,
            sede=sede,
            is_sede_legale=False,
        )
        assoc2.clean()  # Non deve sollevare eccezioni


def test_validate_codice_fiscale_valid():
    """Test validazione codice fiscale valido."""
    # Codice fiscale valido di esempio
    validate_codice_fiscale('RSSMRA80A01H501U')


def test_validate_codice_fiscale_invalid():
    """Test validazione codice fiscale non valido."""
    with pytest.raises(ValidationError):
        validate_codice_fiscale('INVALID')


@pytest.mark.django_db
def test_validate_p_iva_italiana_invalid():
    """Test validazione P.IVA non valida."""
    with pytest.raises(ValidationError):
        validate_p_iva_italiana('00000000000')
