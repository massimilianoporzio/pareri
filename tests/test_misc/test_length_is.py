"""Test per il custom template tag length_is."""

from server.common.django.templatetags.length_is import length_is

# pylint: disable=unused-argument


def test_length_is_true():
    """Testa casi in cui length_is dovrebbe restituire True."""
    assert length_is([1, 2, 3], 3) is True
    assert length_is('abc', 3) is True
    assert length_is((1, 2), 2) is True


def test_length_is_false():
    """Testa casi in cui length_is dovrebbe restituire False."""
    assert length_is([1, 2, 3], 2) is False
    assert length_is('abc', 2) is False
    assert length_is((1, 2), 3) is False


def test_length_is_exception():
    """Testa casi in cui dovrebbe gestire eccezioni e restituire False."""

    class NoLen:
        """Classe senza __len__."""

    assert length_is(NoLen(), 1) is False
    assert length_is([1, 2, 3], 'not_a_number') is False
