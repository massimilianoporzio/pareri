import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
import django

django.setup()

from django.conf import settings
from django.contrib.auth.models import Group


def main():
    """Crea il gruppo di accesso completo se non esiste."""
    group_name = getattr(
        settings, 'FULL_ACCESS_GROUP_NAME', 'Full Access Admin'
    )
    _, created = Group.objects.get_or_create(name=group_name)
    if created:
        print(f'Creato gruppo: {group_name}')
    else:
        print(f"Il gruppo '{group_name}' esiste già.")


if __name__ == '__main__':
    main()
