"""
Django settings for server project.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their config, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

from django.utils.translation import gettext_lazy as _

from server.settings.components import BASE_DIR, config

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

SECRET_KEY = config('DJANGO_SECRET_KEY')

# Application definition:


# --- Project apps ---
PROJECT_APPS: tuple[str, ...] = (
    'server.apps.main',
    'server.apps.accounts',
    'server.apps.datoriLavoro',
    'server.common',
    'server.common.django',
    'server.apps.theme',
)

# --- Third-party apps ---
THIRD_PARTY_APPS: tuple[str, ...] = (
    'axes',
    'health_check',
    'health_check.db',
    'health_check.cache',
    'health_check.storage',
    'jazzmin',
    'cities_light',  # Django-cities-light for geographic data
    'tailwind',
    'django_browser_reload',
)

# --- Django core apps ---
DJANGO_CORE_APPS: tuple[str, ...] = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
)

INSTALLED_APPS: tuple[str, ...] = (
    PROJECT_APPS + THIRD_PARTY_APPS + DJANGO_CORE_APPS
)

TAILWIND_APP_NAME = 'server.apps.theme'
NPM_BIN_PATH = config('NPM_BIN_PATH', default='/usr/bin/npm')

JAZZMIN_SETTINGS = {
    # css per cambiare qualche elemento
    'custom_css': 'css/admin.css',
    # title of the window
    'site_title': 'Pratiche & Pareri',
    # Title on the login screen (19 chars max)
    'site_header': 'Pratiche & Pareri',
    # Title on the brand (19 chars max)
    'site_brand': 'Pratiche & Pareri',
    # Logo to use for your site, must be present in static files
    'site_logo': 'images/icon.png',
    # Logo to use for your site, must be present in static files
    'login_logo': 'images/logo2.png',
    # Logo to use for login form in dark themes (defaults to login_logo)
    'login_logo_dark': 'images/logo2.png',
    # CSS classes that are applied to the logo above
    'site_logo_classes': 'img-circle  bg-transparent',
    # Welcome text on the login screen
    'welcome_sign': 'Benvenuti su Pratiche&Pareri',
    # Copyright on the footer
    'copyright': 'Massimiliano Porzio',
    # Whether to link font from google (use custom_css to supply font otherwise)
    'use_google_fonts_cdn': True,
    # Whether to show the UI customizer on the sidebar
    'show_ui_builder': True,
    # abilita traduzione in jazzmin
    'i18n_enabled': True,
    # Enable related object modal instead of full page
    'related_modal_active': True,
    # Make the modal small as requested
    'related_modal_classes': 'modal-dialog modal-sm',
    # icons for apps:
    'icons': {
        # Cities-light proxy models (app_label = cities_light)
        'cities_light.CityProxy': 'fas fa-city',
        # Nazioni (CountryProxy) - use FA5 icon
        'cities_light.CountryProxy': 'fas fa-globe-europe',
        'cities_light.RegionProxy': 'fas fa-map-marker-alt',
        # Pareri app models (TODO: verificare app_label corretto)
        'pareri.TipoOrigine': 'fas fa-building-columns',
        'pareri.EspertoRadioprotezione': 'fas fa-radiation',
        'pareri.TipoPratica': 'fas fa-file-invoice',
        'pareri.TipoProcesso': 'fas fa-gear',
        # Accounts app
        'accounts.CustomUser': 'fas fa-user',
        # Auth app
        'auth.Group': 'fas fa-users',
        'auth.Permission': 'fas fa-key',
        'axes.AccessAttempt': 'fas fa-sign-in-alt',
        'axes.AccessLog': 'fas fa-edit',
        'axes.AccessFailureLog': 'fas fa-ban',
        # Admin app (voci di Log)
        'admin.LogEntry': 'fas fa-history',
        # DatoriLavoro app (use FA5-compatible icon)
        'datoriLavoro.Sede': 'fas fa-map-marker-alt',
        'datoriLavoro.DatoreLavoro': 'fas fa-user-tie',
    },
    'show_logout': False,
}
JAZZMIN_UI_TWEAKS = {
    'navbar_small_text': False,
    'footer_small_text': False,
    'body_small_text': False,
    'brand_small_text': False,
    'brand_colour': 'navbar-pink',
    'navbar': 'navbar-white navbar-light',
    'no_navbar_border': False,
    'navbar_fixed': False,
    'layout_boxed': False,
    'footer_fixed': True,
    'sidebar_fixed': False,
    'sidebar': 'sidebar-dark-maroon',
    'sidebar_nav_small_text': False,
    'sidebar_disable_expand': False,
    'sidebar_nav_child_indent': False,
    'sidebar_nav_compact_style': False,
    'sidebar_nav_legacy_style': False,
    'sidebar_nav_flat_style': False,
    'theme': 'default',
    'dark_mode_theme': None,
    'button_classes': {
        'primary': 'btn-info',
        'secondary': 'btn-secondary',
        'info': 'btn-info',
        'warning': 'btn-warning',
        'danger': 'btn-danger',
        'success': 'btn-success',
    },
}


MIDDLEWARE: tuple[str, ...] = (
    # Whitenoise per servire file STATICFILES_DIRS
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # Logging:
    'server.settings.components.logging.LoggingContextVarsMiddleware',
    # Content Security Policy:
    'csp.middleware.CSPMiddleware',
    # Django:
    'django.middleware.security.SecurityMiddleware',
    # django-permissions-policy
    'django_permissions_policy.PermissionsPolicyMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Axes:
    'axes.middleware.AxesMiddleware',
    # CRUM - Current Request User Middleware:
    'crum.CurrentRequestUserMiddleware',
    # django-browser-reload
    'django_browser_reload.middleware.BrowserReloadMiddleware',
)

ROOT_URLCONF = 'server.urls'

WSGI_APPLICATION = 'server.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DB'),
        'USER': config('POSTGRES_USER'),
        'PASSWORD': config('POSTGRES_PASSWORD'),
        'HOST': config('DJANGO_DATABASE_HOST'),
        'PORT': config('DJANGO_DATABASE_PORT', cast=int),
        'CONN_MAX_AGE': config('CONN_MAX_AGE', cast=int, default=60),
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c statement_timeout=15000ms',
            # consider using 'isolation_level' set to 'serializable'
        },
    },
}

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

USE_I18N = True

LANGUAGES = (
    ('en', _('English')),
    ('it', _('Italian')),
)

LOCALE_PATHS = ('locale/',)

USE_TZ = True
TIME_ZONE = 'UTC'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/pareri/static/'
STATICFILES_DIRS = [BASE_DIR / 'server' / 'static']
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Directory dove Django raccoglie tutti i file statici delle app
STATIC_ROOT = BASE_DIR.joinpath('server', 'staticfiles')


# Templates
# https://docs.djangoproject.com/en/5.2/ref/templates/api

TEMPLATES = [
    {
        'APP_DIRS': True,
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'server' / 'templates',
            # pagine 404 e 500
            BASE_DIR / 'server' / 'apps' / 'theme' / 'static_src',
            # Contains plain text templates, like `robots.txt`:
            BASE_DIR.joinpath('server', 'common', 'django', 'templates'),
        ],
        'OPTIONS': {
            'context_processors': [
                # Default template context processors:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
        },
    },
]


# Media files
# Media root dir is commonly changed in production
# (see development.py and production.py).
# https://docs.djangoproject.com/en/5.2/topics/files/

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR.joinpath('media')


# Django authentication system
# https://docs.djangoproject.com/en/5.2/topics/auth/

AUTHENTICATION_BACKENDS = (
    'axes.backends.AxesBackend',
    'django.contrib.auth.backends.ModelBackend',
)

# Use the project's custom user model defined in accounts app
# AUTH_USER_MODEL must be 'app_label.ModelName' not a dotted module path
AUTH_USER_MODEL = 'accounts.CustomUser'

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
]


# Security
# https://docs.djangoproject.com/en/5.2/topics/security/

SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

X_FRAME_OPTIONS = 'DENY'

# https://docs.djangoproject.com/en/3.0/ref/middleware/#referrer-policy
# https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Referrer-Policy
SECURE_REFERRER_POLICY = 'same-origin'

# https://github.com/adamchainz/django-permissions-policy#setting
PERMISSIONS_POLICY: dict[str, str | list[str]] = {}

# CSRF trusted origins (usa DOMAIN_NAME dal file .env)


CSRF_TRUSTED_ORIGINS = [
    f'http://{config("DOMAIN_NAME")}',
]

# Timeouts
# https://docs.djangoproject.com/en/5.2/ref/settings/#std:setting-EMAIL_TIMEOUT

EMAIL_TIMEOUT = 5

FULL_ACCESS_GROUP_NAME = config(
    'FULL_ACCESS_GROUP_NAME', default='Full Access Admin'
)

# Name for the limited admin group (staff with CRUD on selected apps)
REGULAR_ADMIN_GROUP_NAME = config(
    'REGULAR_ADMIN_GROUP_NAME', default='Regular Admin'
)

# Admin visibility control: app labels visible to restricted users.
# Configure via .env as a comma-separated list.
# Example env value: "ADMIN_AUTHORIZED_APPS=pareri,datoriLavoro".
# Notes:
# - Values must match each app's app_label (usually the last module path
#   segment or AppConfig.label).
# - Users outside FULL_ACCESS_GROUP_NAME will only see apps listed here.
_ADMIN_AUTHORIZED_APPS = config(
    'ADMIN_AUTHORIZED_APPS', default='pareri,datoriLavoro'
)
AUTHORIZED_APPS: list[str] = [
    app.strip() for app in _ADMIN_AUTHORIZED_APPS.split(',') if app.strip()
]


# Django-cities-light configuration
# https://django-cities-light.readthedocs.io/
# ============================================================================

# Import only Italian geographic data
CITIES_LIGHT_TRANSLATION_LANGUAGES = ['it']
CITIES_LIGHT_INCLUDE_COUNTRIES = ['IT']

# Use cities with 500+ inhabitants for better coverage
CITIES_LIGHT_CITY_SOURCES = [
    'http://download.geonames.org/export/dump/cities500.zip',
]

# Enable geocoding features
CITIES_LIGHT_ENABLE_GEOCODING = True

# Ignore auto-named migrations from third party apps
# (for django-test-migrations)
DTM_IGNORED_MIGRATIONS = [
    'cities_light.0003_auto_20141120_0342',
    'cities_light.0010_auto_20200508_1851',
    'cities_light.0013_cityproxy_countryproxy_regionproxy',
]
