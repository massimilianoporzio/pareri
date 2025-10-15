"""Project-level integration tests."""
# pylint: disable=unused-argument

import importlib


def test_asgi_and_wsgi_importable():
    """ASGI and WSGI modules must be importable.

    Ensure both expose ``application`` objects.
    """
    asgi = importlib.import_module('server.asgi')
    wsgi = importlib.import_module('server.wsgi')

    assert hasattr(asgi, 'application')
    assert hasattr(wsgi, 'application')
