import uuid

from concurrency.fields import IntegerVersionField
from crum import get_current_user
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    """
    We use this for all the models.

    making all models inherit from it (apart from CustomUser)
    """

    id = models.UUIDField(
        _('id'), primary_key=True, default=uuid.uuid4, editable=False
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_%(class)s_set',
    )
    created_by_fullname = models.CharField(max_length=150, blank=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_%(class)s_set',
    )
    updated_by_fullname = models.CharField(max_length=150, blank=True)
    version = IntegerVersionField()
    is_active = models.BooleanField(
        default=True, verbose_name=_('ancora attivo')
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Overrides the default save method.

        This automatically set the user and their full name
        for created_by and updated_by fields based on the current user context.
        """
        user = get_current_user()
        if user and not user.is_anonymous:
            # Imposta created_by solo se non è già stato impostato
            if self.created_by is None:
                self.created_by = user
                self.created_by_fullname = (
                    user.nome_utente
                    if hasattr(user, 'nome_utente')
                    else str(user)
                )
            # L'utente che ha fatto l'ultima modifica è sempre l'utente corrente
            self.updated_by = user
            self.updated_by_fullname = (
                user.nome_utente if hasattr(user, 'nome_utente') else str(user)
            )
        super().save(*args, **kwargs)
