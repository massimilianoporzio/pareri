import contextlib

from django.conf import settings
from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from server.apps.accounts.admin import CustomUserAdmin
from server.apps.accounts.models import CustomUser
from server.apps.main.admin import BlogPostAdmin
from server.apps.main.models import BlogPost, DummyModel

# Definisci la lista delle app autorizzate per gli altri superuser
AUTHORIZED_APPS = [
    'pareri',
    # Aggiungi qui gli 'app_label' delle app che vuoi mostrare
]


class CustomAdminSite(admin.AdminSite):
    """Custom Admin Site with personalized headers and titles."""

    site_header = 'Pareri Custom Admin'
    site_title = 'Pareri Admin Portal'
    index_title = "Benvenuto nell'area amministrativa"

    def get_app_list(self, request):
        """Personalizza la lista delle app visibili.

        Lo fa in base ai gruppi dell'utente.
        """
        app_list = super().get_app_list(request)
        # Controlla se l'utente appartiene al gruppo "Full Access Admin"
        user_has_full_access_group = (
            request.user.is_superuser
            and request.user.groups.filter(
                name=settings.FULL_ACCESS_GROUP_NAME
            ).exists()
        )

        if user_has_full_access_group:
            return app_list
        return [app for app in app_list if app['app_label'] in AUTHORIZED_APPS]


custom_admin_site = CustomAdminSite(name='custom_admin')

# Registrazione del modello CustomUser

custom_admin_site.register(CustomUser, CustomUserAdmin)


class GroupAdmin(admin.ModelAdmin):
    """Admin per il modello Group con filtro orizzontale per i permessi."""

    filter_horizontal = ('permissions',)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """Ottimizza la query per i permessi."""
        if db_field.name == 'permissions':
            kwargs['queryset'] = Permission.objects.select_related(
                'content_type'
            ).all()
        return super().formfield_for_manytomany(db_field, request, **kwargs)


class PermissionAdmin(admin.ModelAdmin):
    """Ottimizza la queryset per Permission per evitare N+1 su content_type."""

    def get_queryset(self, request):
        """Restituisce una queryset con content_type prefetchato."""
        return super().get_queryset(request).select_related('content_type')


custom_admin_site.register(Group, GroupAdmin)
custom_admin_site.register(Permission, PermissionAdmin)
custom_admin_site.register(ContentType)
custom_admin_site.register(LogEntry)

custom_admin_site.register(BlogPost, BlogPostAdmin)
custom_admin_site.register(DummyModel)
try:
    from axes.models import AccessAttempt, AccessFailureLog, AccessLog
    from django.contrib.admin.sites import AlreadyRegistered
    from django.http import HttpResponseForbidden

    class ForbiddenAddAdmin(admin.ModelAdmin):
        """Admin che restituisce 403 Forbidden sulla pagina di add."""

        def add_view(self, request, form_url='', extra_context=None):
            """Disabilita la pagina di add restituendo 403 Forbidden."""
            return HttpResponseForbidden()

    for model in (AccessAttempt, AccessLog, AccessFailureLog):
        with contextlib.suppress(AlreadyRegistered):
            custom_admin_site.register(model, ForbiddenAddAdmin)
except ImportError:
    pass
