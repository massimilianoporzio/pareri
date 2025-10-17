"""Tests for django-cities-light management commands."""

from io import StringIO
from unittest.mock import patch

import pytest
from cities_light.models import Region
from django.core.management import call_command

from server.apps.main.models import CityProxy, CountryProxy, RegionProxy


@pytest.mark.django_db
def test_translate_italian_regions_country_success():
    """Test successful country translation."""
    # Create Italy with English name
    CountryProxy.objects.create(
        name='Italy', code2='IT', code3='ITA', slug='italy'
    )

    out = StringIO()
    call_command('translate_italian_regions', stdout=out)

    # Check country was translated
    country = CountryProxy.objects.get(code2='IT')
    assert country.name == 'Italia'
    assert 'Italy' in country.alternate_names
    assert '✓ Updated country: Italy → Italia' in out.getvalue()


@pytest.mark.django_db
def test_translate_italian_regions_country_not_found():
    """Test country translation when Italy doesn't exist."""
    out = StringIO()
    call_command('translate_italian_regions', stdout=out)

    assert '⚠ Country Italy not found' in out.getvalue()


@pytest.mark.django_db
def test_translate_italian_regions_region_success():
    """Test successful region translation."""
    # Create Italy and a region with English name
    country = CountryProxy.objects.create(
        name='Italy', code2='IT', code3='ITA', slug='italy'
    )
    RegionProxy.objects.create(
        name='Lombardy', country=country, slug='lombardy'
    )

    out = StringIO()
    call_command('translate_italian_regions', stdout=out)

    # Check region was translated
    region = RegionProxy.objects.get(slug='lombardy')
    assert region.name == 'Lombardia'
    assert 'Lombardy' in region.alternate_names
    assert '✓ Updated region: Lombardy → Lombardia' in out.getvalue()


@pytest.mark.django_db
def test_translate_italian_regions_region_not_found():
    """Test region translation when region doesn't exist."""
    # Create Italy but no regions
    CountryProxy.objects.create(
        name='Italy', code2='IT', code3='ITA', slug='italy'
    )

    out = StringIO()
    call_command('translate_italian_regions', stdout=out)

    # Should warn about missing regions
    assert '⚠ Region not found:' in out.getvalue()


@pytest.mark.django_db
def test_translate_italian_regions_multiple_regions():
    """Test handling of MultipleObjectsReturned exception.

    Note: This test uses unittest.mock to simulate the rare case where
    multiple regions with the same name exist, since the database constraint
    prevents creating actual duplicates.
    """
    # Create Italy and a region
    country = CountryProxy.objects.create(
        name='Italy', code2='IT', code3='ITA', slug='italy'
    )
    RegionProxy.objects.create(
        name='The Marches', country=country, slug='marches'
    )

    # Mock to simulate MultipleObjectsReturned for only The Marches
    original_get = Region.objects.get

    def mock_get(*args, **kwargs):
        if kwargs.get('name') == 'The Marches':
            raise Region.MultipleObjectsReturned
        return original_get(*args, **kwargs)

    with patch.object(Region.objects, 'get', side_effect=mock_get):
        out = StringIO()
        call_command('translate_italian_regions', stdout=out)

        # Should error on multiple regions
        assert '✗ Multiple regions found: The Marches' in out.getvalue()


@pytest.mark.django_db
def test_translate_italian_regions_city_display_names():
    """Test city display names are updated correctly."""
    # Create Italy, region, and city
    country = CountryProxy.objects.create(
        name='Italy', code2='IT', code3='ITA', slug='italy'
    )
    region = RegionProxy.objects.create(
        name='Lombardy', country=country, slug='lombardy'
    )
    city = CityProxy.objects.create(
        name='Milano',
        region=region,
        country=country,
        slug='milano',
        display_name='Milano, Lombardy, Italy',
    )

    out = StringIO()
    call_command('translate_italian_regions', stdout=out)

    # Check city display_name was updated
    city.refresh_from_db()
    assert city.display_name == 'Milano, Lombardia, Italia'
    assert 'city display names updated' in out.getvalue()


@pytest.mark.django_db
def test_translate_italian_regions_many_cities_progress():
    """Test progress feedback with many cities (>100)."""
    # Create Italy and region
    country = CountryProxy.objects.create(
        name='Italy', code2='IT', code3='ITA', slug='italy'
    )
    region = RegionProxy.objects.create(
        name='Lombardy', country=country, slug='lombardy'
    )

    # Create 150 cities to test progress feedback every 100
    for i in range(150):
        CityProxy.objects.create(
            name=f'City{i}',
            region=region,
            country=country,
            slug=f'city{i}',
            display_name=f'City{i}, Lombardy, Italy',
        )

    out = StringIO()
    call_command('translate_italian_regions', stdout=out)

    output = out.getvalue()

    # Check progress was shown at 100 cities
    assert 'Updated 100/150 cities' in output
    assert 'Updated 150/150 cities' in output
    assert '150 city display names updated' in output


@pytest.mark.django_db
def test_translate_italian_regions_complete_workflow():
    """Test complete translation workflow with country, region, and city."""
    # Create complete Italian geographic structure
    country = CountryProxy.objects.create(
        name='Italy', code2='IT', code3='ITA', slug='italy'
    )
    region = RegionProxy.objects.create(
        name='The Marches', country=country, slug='marches'
    )
    CityProxy.objects.create(
        name='Ancona',
        region=region,
        country=country,
        slug='ancona',
        display_name='Ancona, The Marches, Italy',
    )

    out = StringIO()
    call_command('translate_italian_regions', stdout=out)

    output = out.getvalue()

    # Verify country translation
    country.refresh_from_db()
    assert country.name == 'Italia'

    # Verify region translation
    region.refresh_from_db()
    assert region.name == 'Marche'

    # Verify city display_name
    city = CityProxy.objects.get(slug='ancona')
    assert city.display_name == 'Ancona, Marche, Italia'

    # Verify success messages
    assert '✓ Translation completed successfully!' in output
    assert '1 country translated' in output
    assert 'regions translated' in output


@pytest.mark.django_db
def test_translate_italian_regions_preserves_existing_alternate_names():
    """Test that existing alternate_names are preserved."""
    # Create country with existing alternate names
    country = CountryProxy.objects.create(
        name='Italy',
        code2='IT',
        code3='ITA',
        slug='italy',
        alternate_names='Repubblica Italiana',
    )
    region = RegionProxy.objects.create(
        name='Lombardy',
        country=country,
        slug='lombardy',
        alternate_names='Lombardei',
    )

    out = StringIO()
    call_command('translate_italian_regions', stdout=out)

    # Check alternate names were preserved and appended
    country.refresh_from_db()
    assert 'Repubblica Italiana' in country.alternate_names
    assert 'Italy' in country.alternate_names

    region.refresh_from_db()
    assert 'Lombardei' in region.alternate_names
    assert 'Lombardy' in region.alternate_names


@pytest.mark.django_db
def test_translate_italian_regions_all_20_regions():
    """Test that all 20 Italian regions can be translated."""
    # Create Italy
    country = CountryProxy.objects.create(
        name='Italy', code2='IT', code3='ITA', slug='italy'
    )

    # Create all 20 regions with English names from ITALIAN_REGIONS mapping
    english_names = [
        'Abruzzo',
        'Aosta Valley',
        'Apulia',
        'Basilicate',
        'Calabria',
        'Campania',
        'Emilia-Romagna',
        'Friuli Venezia Giulia',
        'Lazio',
        'Liguria',
        'Lombardy',
        'The Marches',
        'Molise',
        'Piedmont',
        'Sardinia',
        'Sicily',
        'Trentino-Alto Adige',
        'Tuscany',
        'Umbria',
        'Veneto',
    ]

    for i, name in enumerate(english_names, 1):
        RegionProxy.objects.create(
            name=name,
            country=country,
            slug=f'region-{i}',
        )

    out = StringIO()
    call_command('translate_italian_regions', stdout=out)

    output = out.getvalue()

    # Verify all regions were translated
    assert '20 regions translated' in output

    # Check a few specific translations
    lombardy = RegionProxy.objects.get(slug='region-11')
    assert lombardy.name == 'Lombardia'

    marches = RegionProxy.objects.get(slug='region-12')
    assert marches.name == 'Marche'

    apulia = RegionProxy.objects.get(slug='region-3')
    assert apulia.name == 'Puglia'
