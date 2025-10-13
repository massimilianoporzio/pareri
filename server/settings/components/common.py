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
    'server.common',
    'server.common.django',
)

# --- Third-party apps ---
THIRD_PARTY_APPS: tuple[str, ...] = (
    'axes',
    'health_check',
    'health_check.db',
    'health_check.cache',
    'health_check.storage',
    'jazzmin',
)

# --- Django core apps ---
DJANGO_CORE_APPS: tuple[str, ...] = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
)

INSTALLED_APPS: tuple[str, ...] = (
    PROJECT_APPS + THIRD_PARTY_APPS + DJANGO_CORE_APPS
)

MIDDLEWARE: tuple[str, ...] = (
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
    ('ru', _('Russian')),
)

LOCALE_PATHS = ('locale/',)

USE_TZ = True
TIME_ZONE = 'UTC'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/pareri/static/'

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
