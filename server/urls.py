"""
Main URL mapping configuration file.

Include other URLConfs from external apps using method `include()`.

It is also a good practice to keep a single URL to the root index page.

This examples uses Django's default media
files serving technique in development.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib.admindocs import urls as admindocs_urls
from django.urls import include, path
from django.views.generic import TemplateView
from health_check import urls as health_urls

from server.admin import custom_admin_site
from server.apps.main import urls as main_urls

urlpatterns = [
    # Apps:
    path('main/', include(main_urls, namespace='main')),
    # Health checks:
    path('health/', include(health_urls)),
    # django-admin:
    path('pareri/doc/', include(admindocs_urls)),
    path('pareri/', custom_admin_site.urls),
    # Text and xml static files:
    path(
        'robots.txt',
        TemplateView.as_view(
            template_name='common/txt/robots.txt',
            content_type='text/plain',
        ),
    ),
    path(
        'humans.txt',
        TemplateView.as_view(
            template_name='common/txt/humans.txt',
            content_type='text/plain',
        ),
    ),
    # It is a good practice to have explicit index view:
    # Not in this case we want the site on http://<ip>/pareri/
]

if settings.DEBUG:  # pragma: no cover
    import debug_toolbar

    urlpatterns = [
        # URLs specific only to django-debug-toolbar:
        path('__debug__/', include(debug_toolbar.urls)),
        *urlpatterns,
        # Serving media files in development only:
        *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    ]
