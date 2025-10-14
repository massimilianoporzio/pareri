from server.common.django.templatetags.length_is import length_is


def test_length_is_true():
    assert length_is([1, 2, 3], 3) is True
    assert length_is('abc', 3) is True
    assert length_is((1, 2), 2) is True


def test_length_is_false():
    assert length_is([1, 2, 3], 2) is False
    assert length_is('abc', 2) is False
    assert length_is((1, 2), 3) is False


def test_length_is_exception():
    class NoLen:
        pass

    assert length_is(NoLen(), 1) is False
    assert length_is([1, 2, 3], 'not_a_number') is False
