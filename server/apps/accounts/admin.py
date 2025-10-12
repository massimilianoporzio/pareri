"""Admin module.

Questo modulo fornisce funzionalità per admin.
"""

from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Permission
from django.db.models import Prefetch

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin interface for CustomUser model."""

    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = (
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'is_active',
        'date_joined',
    )

    list_filter = (
        'is_staff',
        'is_active',
        'date_joined',
        'is_superuser',
        'gender',
        'groups',
    )

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            'Informazioni personali',
            {'fields': ('first_name', 'last_name', 'gender')},
        ),
        (
            'Permessi',
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                )
            },
        ),
        ('Date importanti', {'fields': ('last_login', 'date_joined')}),
        (
            'Audit',
            {'fields': ('created_by', 'updated_by'), 'classes': ('collapse',)},
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'email',
                    'password',
                    'password2',
                    'first_name',
                    'last_name',
                    'gender',
                    'is_staff',
                    'is_active',
                    'groups',
                ),
            },
        ),
    )

    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

    readonly_fields = ('created_by', 'updated_by', 'date_joined', 'last_login')
    filter_horizontal = ('groups', 'user_permissions')

    def get_queryset(self, request):
        """Return a queryset that prefetches related objects.

        Accessing related permissions/content types in admin templates
        can cause N+1 queries; prefetch them here to avoid that.
        """
        # Prefetch groups and user_permissions, and ensure
        # Permission.content_type is selected to avoid per-row queries when
        # templates access it.
        prefetch_user_perms = Prefetch(
            'user_permissions',
            queryset=Permission.objects.select_related('content_type'),
        )
        prefetch_group_perms = Prefetch(
            'groups__permissions',
            queryset=Permission.objects.select_related('content_type'),
        )

        return (
            super()
            .get_queryset(request)
            .prefetch_related(
                'groups', prefetch_user_perms, prefetch_group_perms
            )
        )

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Override change_view and provide recent log entries.

        Recent LogEntry instances are loaded with select_related to avoid
        N+1 when templates access their content_type and user.
        """
        extra_context = extra_context or {}
        recent = (
            LogEntry.objects.filter(object_id=object_id)
            .select_related('content_type', 'user')
            .order_by('-action_time')[:20]
        )
        extra_context.setdefault('recent_log_entries', recent)
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context
        )

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """Provide optimized querysets for many-to-many fields used in forms.

        Specifically ensure permission choices have their content_type
        selected to avoid per-row queries during widget rendering.
        """
        if db_field.name == 'user_permissions':
            kwargs['queryset'] = Permission.objects.select_related(
                'content_type'
            ).all()
        return super().formfield_for_manytomany(db_field, request, **kwargs)
