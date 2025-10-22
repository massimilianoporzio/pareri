from __future__ import annotations

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandParser
from django.db import transaction


class Command(BaseCommand):
    """Create/update a group with CRUD perms for selected apps.

    The command grants add/change/delete/view permissions on all managed,
    non-proxy models for the provided app labels (defaults to
    settings.AUTHORIZED_APPS). Optionally assigns users to the group.
    """

    help = (
        'Create or update a group with CRUD permissions for selected apps '
        '(default: settings.AUTHORIZED_APPS) and optionally assign users.'
    )

    def add_arguments(self, parser: CommandParser) -> None:
        """Define CLI arguments for the management command."""
        parser.add_argument(
            '--group-name',
            default=getattr(
                settings, 'REGULAR_ADMIN_GROUP_NAME', 'Regular Admin'
            ),
            help='Name of the group to create/update.',
        )
        parser.add_argument(
            '--apps',
            nargs='*',
            default=getattr(settings, 'AUTHORIZED_APPS', []),
            help=(
                'App labels to grant CRUD permissions for. '
                'Defaults to settings.AUTHORIZED_APPS.'
            ),
        )
        parser.add_argument(
            '--assign-users',
            nargs='*',
            default=[],
            help='Usernames or emails to assign to the group (optional).',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show actions without applying changes.',
        )

    # ------------------------ helpers ------------------------
    def _collect_perms(
        self, app_labels: list[str]
    ) -> tuple[set[Permission], list[str]]:
        perms_to_set: set[Permission] = set()
        missing_apps: list[str] = []

        for app_label in app_labels:
            try:
                app_config = apps.get_app_config(app_label)
            except LookupError:
                missing_apps.append(app_label)
                continue
            for model in app_config.get_models():
                # Skip proxy or unmanaged models
                if (
                    getattr(model._meta, 'proxy', False)  # noqa: SLF001
                    or not getattr(model._meta, 'managed', True)  # noqa: SLF001
                ):
                    continue  # pragma: no cover
                ct = ContentType.objects.get_for_model(model)
                codenames = [
                    f'add_{model._meta.model_name}',  # noqa: SLF001
                    f'change_{model._meta.model_name}',  # noqa: SLF001
                    f'delete_{model._meta.model_name}',  # noqa: SLF001
                    f'view_{model._meta.model_name}',  # noqa: SLF001
                ]
                perms = Permission.objects.filter(
                    content_type=ct, codename__in=codenames
                )
                perms_to_set.update(perms)
        return perms_to_set, missing_apps  # pragma: no cover

    def _assign_users_to_group(
        self, identifiers: list[str], group: Group
    ) -> list[str]:
        """Assign users by username or email to the given group."""
        user_model = get_user_model()
        assigned: list[str] = []
        for identifier in identifiers:
            user = None
            try:
                user = user_model.objects.get(username=identifier)
            except user_model.DoesNotExist:  # type: ignore[attr-defined]
                try:
                    user = user_model.objects.get(email=identifier)
                except user_model.DoesNotExist:  # type: ignore[attr-defined]
                    self.stdout.write(
                        self.style.WARNING(f'User not found: {identifier}')
                    )
                    continue
            user.groups.add(group)
            assigned.append(identifier)
        return assigned

    # ------------------------ main ------------------------
    def handle(self, *args, **options):  # type: ignore[override]  # noqa: C901
        """Execute the command."""
        group_name: str = options['group_name']
        app_labels: list[str] = [
            a.strip() for a in options['apps'] if a.strip()
        ]
        assign_users: list[str] = options['assign_users']
        dry_run: bool = options['dry_run']

        if not app_labels:
            self.stdout.write(
                self.style.WARNING('No app labels provided; nothing to do.')
            )
            return  # pragma: no cover

        if dry_run:
            self.stdout.write(self.style.WARNING('Running in dry-run mode.'))

        perms_to_set, missing_apps = self._collect_perms(app_labels)
        if missing_apps:  # pragma: no branch
            self.stdout.write(
                self.style.WARNING(
                    'Skipping unknown apps: '
                    + ', '.join(sorted(set(missing_apps)))
                )
            )

        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    "Would create/update group '"
                    + group_name
                    + f"' with {len(perms_to_set)} permissions"
                )
            )
            if assign_users:
                self.stdout.write(
                    self.style.SUCCESS(
                        'Would assign users: ' + ', '.join(assign_users)
                    )
                )
            return  # pragma: no cover

        with transaction.atomic():
            group, _ = Group.objects.get_or_create(name=group_name)
            group.permissions.set(perms_to_set)
            group.save()

            assigned_users: list[str] = []
            if assign_users:
                assigned_users = self._assign_users_to_group(
                    assign_users, group
                )

        self.stdout.write(
            self.style.SUCCESS(
                "Group '"
                + group_name
                + f"' updated with {len(perms_to_set)} permissions."
            )
        )
        if assign_users:
            self.stdout.write(
                self.style.SUCCESS(
                    'Assigned users: ' + ', '.join(assigned_users)
                )
            )
