import contextlib

from django.conf import settings
from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from server.apps.accounts.admin import CustomUserAdmin
from server.apps.accounts.models import CustomUser
from server.apps.main.admin import BlogPostAdmin
from server.apps.main.models import (
    BlogPost,
    CityProxy,
    CountryProxy,
    DummyModel,
    RegionProxy,
)


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
        # Usa la lista di app autorizzate configurata nelle settings
        authorized = getattr(settings, 'AUTHORIZED_APPS', [])
        return [app for app in app_list if app['app_label'] in authorized]


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


# ============================================================================
# Django-cities-light Proxy Models Registration
# ============================================================================


class RegionFilter(admin.SimpleListFilter):
    """Filtro personalizzato per Regione con label italiano."""

    title = 'Regione'  # Label che appare nell'interfaccia admin
    parameter_name = 'region'

    def lookups(self, request, model_admin):
        """Restituisce la lista delle regioni disponibili."""
        regions = RegionProxy.objects.all().order_by('name')
        # Use string ids to align with filter value type and URL params
        return [(str(region.id), region.name) for region in regions]

    def queryset(self, request, queryset):
        """Filtra il queryset in base alla regione selezionata."""
        value = self.value()
        if value is None:
            return queryset
        try:
            region_id = int(value)
        except (TypeError, ValueError):
            return queryset
        return queryset.filter(region_id=region_id)


class CityProxyAdmin(admin.ModelAdmin):
    """Admin per le città italiane."""

    list_display = ('name', 'region', 'country')
    list_filter = (RegionFilter,)  # Usa il filtro personalizzato
    search_fields = ('name', 'alternate_names')
    ordering = ('name',)

    def get_queryset(self, request):
        """Ottimizza la queryset con select_related per evitare N+1."""
        return super().get_queryset(request).select_related('region', 'country')


class RegionProxyAdmin(admin.ModelAdmin):
    """Admin per le regioni italiane."""

    list_display = ('name', 'country')
    search_fields = ('name', 'alternate_names')
    ordering = ('name',)

    def get_queryset(self, request):
        """Ottimizza la queryset con select_related per evitare N+1."""
        return super().get_queryset(request).select_related('country')


class CountryProxyAdmin(admin.ModelAdmin):
    """Admin per i paesi (Italia)."""

    list_display = ('name', 'code2', 'code3')
    search_fields = ('name', 'code2', 'code3')


custom_admin_site.register(CityProxy, CityProxyAdmin)
custom_admin_site.register(RegionProxy, RegionProxyAdmin)
custom_admin_site.register(CountryProxy, CountryProxyAdmin)


# ============================================================================
# Django Axes - Access Control
# ============================================================================

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
