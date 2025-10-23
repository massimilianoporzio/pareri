"""Settings specific for running tests.

Disables debug_toolbar and query_counter.
"""

# Import only the base settings, not development overrides
from server.settings.components.common import *  # noqa

# Remove debug_toolbar and query_counter from INSTALLED_APPS if present
INSTALLED_APPS = tuple(
    app
    for app in INSTALLED_APPS  # noqa: F405
    if app not in {'debug_toolbar', 'query_counter'}
)

# Remove their middleware if present
MIDDLEWARE = tuple(
    mw
    for mw in MIDDLEWARE  # noqa: F405
    if mw
    not in {
        'debug_toolbar.middleware.DebugToolbarMiddleware',
        'query_counter.middleware.DjangoQueryCounterMiddleware',
    }
)

# Use a static secret key for tests
SECRET_KEY = 'test-secret-key'  # noqa: S105
