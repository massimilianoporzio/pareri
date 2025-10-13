from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from server.apps.accounts.admin import CustomUserAdmin
from server.apps.accounts.models import CustomUser


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
        return app_list
        # Altrimenti mostra solo le app autorizzate (personalizza qui)
        # AUTHORIZED_APPS = ['server.apps.main', 'server.apps.accounts']
        # return [app for app in app_list if app['app_label'] in AUTHORIZED_APPS]


custom_admin_site = CustomAdminSite(name='custom_admin')

# Registrazione del modello CustomUser

custom_admin_site.register(CustomUser, CustomUserAdmin)


class GroupAdmin(admin.ModelAdmin):
    filter_horizontal = ('permissions',)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'permissions':
            kwargs['queryset'] = Permission.objects.select_related(
                'content_type'
            ).all()
        return super().formfield_for_manytomany(db_field, request, **kwargs)


custom_admin_site.register(Group, GroupAdmin)
custom_admin_site.register(Permission)
custom_admin_site.register(ContentType)
custom_admin_site.register(LogEntry)
