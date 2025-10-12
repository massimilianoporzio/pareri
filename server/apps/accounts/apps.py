"""App configuration for the accounts app.

Defines the Django AppConfig used to register the accounts application.
"""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """
    Configuration class for the 'accounts' Django application.

    Attributes:
        default_auto_field (str): Specifies the type of auto-created
        primary key field.
        name (str): The name of the application.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'server.apps.accounts'
