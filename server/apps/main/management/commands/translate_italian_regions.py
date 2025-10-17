"""
Management command to translate Italian geographic names.

Translates country and region names from English to Italian.
"""

from typing import ClassVar

from cities_light.models import City, Country, Region
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    """Translate Italian geographic names from English to Italian."""

    help = 'Translates Italian country and region names to Italian'

    # Mapping of English to Italian region names from GeoNames
    ITALIAN_REGIONS: ClassVar[dict[str, str]] = {
        'Abruzzo': 'Abruzzo',
        'Aosta Valley': "Valle d'Aosta",
        'Apulia': 'Puglia',
        'Basilicate': 'Basilicata',
        'Calabria': 'Calabria',
        'Campania': 'Campania',
        'Emilia-Romagna': 'Emilia-Romagna',
        'Friuli Venezia Giulia': 'Friuli-Venezia Giulia',
        'Lazio': 'Lazio',
        'Liguria': 'Liguria',
        'Lombardy': 'Lombardia',
        'The Marches': 'Marche',
        'Molise': 'Molise',
        'Piedmont': 'Piemonte',
        'Sardinia': 'Sardegna',
        'Sicily': 'Sicilia',
        'Trentino-Alto Adige': 'Trentino-Alto Adige',
        'Tuscany': 'Toscana',
        'Umbria': 'Umbria',
        'Veneto': 'Veneto',
    }

    def _update_region(self, english_name: str, italian_name: str) -> bool:
        """Update a single region name."""
        try:
            region = Region.objects.get(
                name=english_name,
                country__code2='IT',
            )
        except Region.DoesNotExist:
            self.stdout.write(
                self.style.WARNING(f'⚠ Region not found: {english_name}')
            )
            return False
        except Region.MultipleObjectsReturned:
            self.stdout.write(
                self.style.ERROR(f'✗ Multiple regions found: {english_name}')
            )
            return False
        else:
            old_name = region.name
            region.name = italian_name
            # Update also alternate_names if needed
            if region.alternate_names:
                region.alternate_names = (
                    f'{region.alternate_names},{english_name}'
                )
            else:
                region.alternate_names = english_name
            region.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Updated region: {old_name} → {italian_name}'
                )
            )
            return True

    def _update_country(self) -> bool:
        """Update Italy country name to Italian."""
        try:
            country = Country.objects.get(code2='IT')
        except Country.DoesNotExist:
            self.stdout.write(self.style.WARNING('⚠ Country Italy not found'))
            return False
        else:
            old_name = country.name
            country.name = 'Italia'
            # Keep English name in alternate_names
            if country.alternate_names:
                country.alternate_names = f'{country.alternate_names},Italy'
            else:
                country.alternate_names = 'Italy'
            country.save()
            self.stdout.write(
                self.style.SUCCESS(f'✓ Updated country: {old_name} → Italia')
            )
            return True

    def _update_city_display_names(self) -> int:
        """Update city display names to reflect new region names."""
        self.stdout.write('\nUpdating city display names...')
        cities = City.objects.filter(country__code2='IT').select_related(
            'region', 'country'
        )

        total_cities = cities.count()
        for i, city in enumerate(cities, 1):
            city.display_name = (
                f'{city.name}, {city.region.name}, {city.country.name}'
            )
            city.save(update_fields=['display_name'])

            # Progress feedback every 100 cities
            if i % 100 == 0 or i == total_cities:
                self.stdout.write(f'  Updated {i}/{total_cities} cities...')

        return total_cities

    def handle(self, *args, **options):
        """Execute the command."""
        self.stdout.write('Starting translation of Italian geographic names...')

        regions_updated = 0
        country_updated = False

        with transaction.atomic():
            # Update country name
            self.stdout.write('\n1. Translating country name...')
            country_updated = self._update_country()

            # Update region names
            self.stdout.write('\n2. Translating region names...')
            for english_name, italian_name in self.ITALIAN_REGIONS.items():
                if self._update_region(english_name, italian_name):
                    regions_updated += 1

            # Update city display_names
            self.stdout.write('\n3. Updating city display names...')
            cities_updated = self._update_city_display_names()

        country_msg = '1 country' if country_updated else '0 countries'
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Translation completed successfully!'
                f'\n  - {country_msg} translated'
                f'\n  - {regions_updated} regions translated'
                f'\n  - {cities_updated} city display names updated'
            )
        )
