import logging
from typing import ClassVar

import codicefiscale as cf
from django.db import models
from django.db.models import Q, UniqueConstraint
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _
from verify_vat_number.vies import get_from_eu_vies

from server.apps.main.models import CityProxy
from server.common.models import BaseModel

logger = logging.getLogger(__name__)


class Sede(BaseModel):
    """Modello per le sedi dei datori di lavoro."""

    nome = models.CharField(max_length=100, blank=False, default='---')
    indirizzo = models.CharField(max_length=255, blank=True, default='')
    citta = models.ForeignKey(
        CityProxy,
        on_delete=models.PROTECT,
        blank=False,
        verbose_name=_('Città'),
    )

    def __str__(self):
        """Rappresentazione stringa della Sede."""
        result = self.nome or 'Anonima'
        return result + ' - ' + str(self.citta)

    class Meta:
        verbose_name = 'Sede'
        verbose_name_plural = 'Sedi'


def validate_p_iva_italiana(value):
    """Valida che la Partita IVA sia italiana e valida."""
    try:
        data = get_from_eu_vies('IT' + value)
        logger.info('P IVA VALIDA? %s', data)

    except Exception as exc:
        raise ValidationError(
            _('%(value)s non è una Partita IVA italiana valida.'),
            params={'value': value},
        ) from exc


def validate_codice_fiscale(value):
    """Valida che il Codice Fiscale sia valido."""
    if not cf.isvalid(value):
        raise ValidationError(
            _('%(value)s non è un Codice Fiscale valido.'),
            params={'value': value},
        )


class DatoreLavoro(BaseModel):
    """Modello per i Datori di Lavoro."""

    ragione_sociale = models.CharField(
        max_length=255,
        verbose_name=_('Ragione Sociale'),
        blank=True,
    )
    p_iva = models.CharField(
        max_length=11,
        verbose_name=_('Partita IVA'),
        blank=True,
        validators=[validate_p_iva_italiana],
    )
    codice_fiscale = models.CharField(
        max_length=16,
        verbose_name=_('Codice Fiscale'),
        blank=True,
        validators=[validate_codice_fiscale],
    )
    # La relazione M2M passa per il modello intermedio
    sedi = models.ManyToManyField(
        Sede,
        through='DatoreLavoroSede',
        related_name='datori_lavoro',
        verbose_name=_('Sedi'),
    )

    def __str__(self):
        """Rappresentazione stringa del Datore di Lavoro."""
        return self.ragione_sociale or self.p_iva or self.codice_fiscale

    class Meta:
        verbose_name = 'Datore di Lavoro'
        verbose_name_plural = 'Datori di Lavoro'

    def clean(self):
        """Validazione personalizzata per DatoreLavoro."""
        super().clean()

        # Richiedi almeno un campo tra ragione_sociale, p_iva, codice_fiscale
        if not any([self.ragione_sociale, self.p_iva, self.codice_fiscale]):
            raise ValidationError(
                'Inserisci almeno uno tra Ragione Sociale, Partita IVA o '
                'Codice Fiscale.'
            )

    def save(self, *args, **kwargs):
        """Override del metodo save per personalizzare il salvataggio."""
        # Assicurati che il codice fiscale sia sempre in maiuscolo
        if self.codice_fiscale:
            self.codice_fiscale = self.codice_fiscale.upper()
        super().save(*args, **kwargs)


class DatoreLavoroSede(BaseModel):
    """Modello intermedio per la relazione tra DatoreLavoro e Sede."""

    datore_lavoro = models.ForeignKey(
        DatoreLavoro,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        db_index=False,
    )
    sede = models.ForeignKey(
        Sede,
        on_delete=models.CASCADE,
        db_index=False,
    )
    is_sede_legale = models.BooleanField(
        default=False, verbose_name=_('Sede Legale?')
    )

    class Meta:
        # Vincoli per garantire l'integrità dei dati
        constraints: ClassVar[list[UniqueConstraint]] = [
            # Una Sede può essere "sede legale" solo per un Datore di Lavoro
            UniqueConstraint(
                fields=['sede', 'is_sede_legale'],
                name='unique_legal_office_for_each_sede',
                condition=Q(is_sede_legale=True),
            ),
            # La stessa sede non può essere associata
            # due volte allo stesso datore di lavoro
            UniqueConstraint(
                fields=['datore_lavoro', 'sede'],
                name='unique_datore_sede',
            ),
        ]

        verbose_name = 'Sede associata'
        verbose_name_plural = 'Sedi asscociate'

    def clean(self):
        """Validazione personalizzata per DatoreLavoroSede."""
        # Impedisce di impostare is_sede_legale a True se la sede
        # è già sede legale per un altro datore di lavoro.
        if self.is_sede_legale:
            qs = DatoreLavoroSede.objects.filter(
                sede=self.sede, is_sede_legale=True
            )
            # Se stiamo modificando un'associazione esistente, escludiamola.
            if self.pk:
                qs = qs.exclude(pk=self.pk)

            if qs.exists():
                raise ValidationError(
                    'Questa sede è già impostata come sede legale per '
                    'un altro datore di lavoro.'
                )
