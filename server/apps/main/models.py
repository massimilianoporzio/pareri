import textwrap
from typing import Final, final, override

from django.db import models

#: That's how constants should be defined.
_POST_TITLE_MAX_LENGTH: Final = 80


@final
class BlogPost(models.Model):
    """
    This model is used just as an example.

    With it we show how one can:
    - Use fixtures and factories
    - Use migrations testing

    """

    title = models.CharField(max_length=_POST_TITLE_MAX_LENGTH)
    body = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # You can probably use `gettext` for this:
        verbose_name = 'BlogPost'  # type: ignore[mutable-override]
        verbose_name_plural = 'BlogPosts'  # type: ignore[mutable-override]

    @override
    def __str__(self) -> str:
        """All django models should have this method."""
        return textwrap.wrap(self.title, _POST_TITLE_MAX_LENGTH // 4)[0]


# Dummy model per test di copertura admin
class DummyModel(models.Model):
    """Dummy model per test di copertura admin."""

    name = models.CharField(max_length=32)
    related = models.ManyToManyField('self', symmetrical=False, blank=True)

    def __str__(self):
        """Rappresentazione stringa del DummyModel."""
        return self.name


# ============================================================================
# Proxy Models for django-cities-light with Italian names
# ============================================================================

from cities_light.models import City, Country, Region  # noqa: E402


class CityProxy(City):
    """Proxy model for City with Italian verbose names."""

    class Meta:
        proxy = True
        verbose_name = 'Città'
        verbose_name_plural = 'Città'
        app_label = 'cities_light'


class RegionProxy(Region):
    """Proxy model for Region with Italian verbose names."""

    class Meta:
        proxy = True
        verbose_name = 'Regione/Provincia'
        verbose_name_plural = 'Regioni/Province'
        app_label = 'cities_light'


class CountryProxy(Country):
    """Proxy model for Country with Italian verbose names."""

    class Meta:
        proxy = True
        verbose_name = 'Nazione'
        verbose_name_plural = 'Nazioni'
        app_label = 'cities_light'
