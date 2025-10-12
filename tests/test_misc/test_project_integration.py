"""Project-level integration tests."""

import importlib

import pytest


def test_asgi_and_wsgi_importable():
    """ASGI and WSGI modules must be importable.

    Ensure both expose ``application`` objects.
    """
    asgi = importlib.import_module('server.asgi')
    wsgi = importlib.import_module('server.wsgi')

    assert hasattr(asgi, 'application')
    assert hasattr(wsgi, 'application')


@pytest.mark.django_db(transaction=False)
def test_index_and_static_texts(client):
    """Index view and text templates (robots/humans) render successfully."""
    # Root index
    resp = client.get('/')
    assert resp.status_code == 200

    # main app hello (from server.apps.main.urls)
    resp2 = client.get('/main/hello/')
    assert resp2.status_code == 200

    # robots and humans text files
    r = client.get('/robots.txt')
    assert r.status_code == 200
    assert b'Technologies' in r.content or len(r.content) > 0

    h = client.get('/humans.txt')
    assert h.status_code == 200
    assert b'Team' in h.content or len(h.content) > 0
