from typing import ClassVar

from django import forms
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from server.admin import custom_admin_site
from server.apps.datoriLavoro.models import DatoreLavoro, DatoreLavoroSede, Sede


class DatoreLavoroSedeInlineFormset(forms.BaseInlineFormSet):
    """Formset personalizzato per gestire le sedi legali."""

    # Ripristina la versione più semplice e sicura
    def clean(self):
        """Ci sia esattamente una sede legale per datore di lavoro."""
        super().clean()

        # Conta quante forme non eliminate hanno is_sede_legale=True
        legal_office_count = sum(
            1
            for form in self.forms
            if form.cleaned_data
            and not form.cleaned_data.get('DELETE', False)
            and form.cleaned_data.get('is_sede_legale', False)
        )

        # Conta quante sedi valide ci sono (non vuote e non cancellate)
        valid_sede_count = sum(
            1
            for form in self.forms
            if form.cleaned_data
            and not form.cleaned_data.get('DELETE', False)
            and form.cleaned_data.get('sede')  # Sede è stata selezionata
        )

        # Richiedi sempre almeno una sede
        if valid_sede_count == 0:
            raise ValidationError(
                'Ogni datore di lavoro deve avere almeno una sede. '
                'Aggiungi una sede e seleziona "Sede Legale?".'
            )

        # Controlla che ci sia esattamente una sede legale
        if legal_office_count == 0:
            raise ValidationError(
                'Ogni datore di lavoro deve avere almeno una sede legale. '
                'Seleziona la casella "Sede Legale?" per una delle sedi.'
            )

        if legal_office_count > 1:
            raise ValidationError(
                'Un datore di lavoro può avere solo una sede legale. '
                'Seleziona la casella "Sede Legale?" solo per una sede.'
            )


class DatoreLavoroSedeInlineForm(forms.ModelForm):
    """Form personalizzato per l'inline delle sedi del datore di lavoro."""

    class Meta:
        model = DatoreLavoroSede
        fields = ('sede', 'is_sede_legale')


class DatoreLavoroSedeInline(admin.TabularInline):
    """Inline admin per le sedi associate ai datori di lavoro."""

    form = DatoreLavoroSedeInlineForm
    model = DatoreLavoroSede
    formset = DatoreLavoroSedeInlineFormset

    extra = 0
    verbose_name = 'Sede associata'
    verbose_name_plural = 'Sedi associate'
    show_change_link = True  # Mostra la matita per modificare la sede
    # Attiva la ricerca e il popup per aggiungere Sede
    autocomplete_fields: ClassVar[list[str]] = ['sede']

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        """Ottimizza il queryset per evitare N+1 e attiva il popup Jazzmin."""
        if db_field.name == 'sede':
            kwargs['queryset'] = Sede.objects.select_related('citta').all()
            kwargs['widget'] = admin.widgets.RelatedFieldWidgetWrapper(
                kwargs.get('widget') or db_field.formfield().widget,
                db_field.remote_field,
                custom_admin_site,
                can_add_related=True,
                can_change_related=True,
                can_delete_related=True,
                can_view_related=True,
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class DatoreLavoroAdminForm(forms.ModelForm):
    """Form personalizzato per l'admin del modello DatoreLavoro."""

    class Meta:
        model = DatoreLavoro
        fields = ('ragione_sociale', 'p_iva', 'codice_fiscale', 'is_active')


@admin.register(DatoreLavoro, site=custom_admin_site)
class DatoreLavoroAdmin(admin.ModelAdmin):
    """Admin per i Datori di Lavoro."""

    form = DatoreLavoroAdminForm
    list_display: ClassVar[list[str]] = [
        'ragione_sociale',
        'p_iva',
        'codice_fiscale',
    ]
    search_fields: ClassVar[list[str]] = [
        'ragione_sociale',
        'p_iva',
        'codice_fiscale',
    ]
    inlines: ClassVar[list] = [DatoreLavoroSedeInline]

    def get_inline_instances(self, request, obj=None):
        """
        Controlla se ci sono già sedi associate e imposta extra = 0.

        Se non ci sono sedi, imposta extra = 1 per forzare la
        visualizzazione della riga.
        """
        inlines = super().get_inline_instances(request, obj)
        for inline in inlines:
            if isinstance(inline, DatoreLavoroSedeInline):
                # Se l'oggetto esiste e ha già delle sedi associate,
                # non mostrare la riga extra
                if obj and obj.datorelavorosede_set.exists():
                    inline.extra = 0
                # Se l'oggetto è nuovo (obj è None) o non ha sedi,
                #  mostrare 1 riga extra
                else:
                    inline.extra = 1
        return inlines

    def save_model(self, request, obj, form, change):
        """Override per personalizzare il salvataggio del modello."""
        # Assicurati che l'istanza principale sia salvata prima
        # di salvare le relazioni.
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        """Override per personalizzare il salvataggio delle relazioni."""
        # A differenza della versione precedente, qui salviamo
        # prima il formset, poi recuperiamo i dati per l'aggiornamento.

        # 1. Salva i formset in linea
        super().save_related(request, form, formsets, change)

        # 2. Esegui la logica di business dopo il salvataggio
        datore_lavoro = form.instance
        legal_sede_pk = None

        # Trova la PK della sede legale che l'utente ha selezionato.
        # Poiché i formset sono già stati salvati,
        # possiamo interrogare il database.
        try:
            legal_sede = datore_lavoro.datorelavorosede_set.get(
                is_sede_legale=True
            )
            legal_sede_pk = legal_sede.pk
        except DatoreLavoroSede.DoesNotExist:
            legal_sede_pk = None
        except DatoreLavoroSede.MultipleObjectsReturned:
            # Gestisce il caso di errore in cui la validazione lato
            # client fallisce.
            # Rimuove tutti i flag tranne il primo (o un altro a tua scelta).
            legal_sedes = datore_lavoro.datorelavorosede_set.filter(
                is_sede_legale=True
            )
            if legal_sedes.exists():
                legal_sede_pk = legal_sedes.first().pk
                legal_sedes.exclude(pk=legal_sede_pk).update(
                    is_sede_legale=False
                )

        # Se è stata trovata una sede legale, aggiorna tutte le altre.
        if legal_sede_pk:
            datore_lavoro.datorelavorosede_set.all().exclude(
                pk=legal_sede_pk
            ).update(is_sede_legale=False)


class SedeAdminForm(forms.ModelForm):
    """Form personalizzato per l'admin del modello Sede."""

    class Meta:
        model = Sede
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        """Inizializza il form con logica personalizzata."""
        super().__init__(*args, **kwargs)

        # Controlla se il form è stato aperto in una finestra pop-up
        # (ovvero, se l'URL contiene il parametro `_popup=1`)
        if self.request and self.request.GET.get('_popup'):
            # Se siamo nel form di creazione di una Sede tramite pop-up,
            # controlliamo le condizioni per spuntare 'is_sede_legale'.
            # L'assunto è che il pop-up dal DatoreLavoro indichi una nuova sede
            # che deve essere legale.
            # Questo è un'euristica, non un controllo a livello di database.
            self.initial['is_sede_legale'] = True


@admin.register(Sede, site=custom_admin_site)
class SedeAdmin(admin.ModelAdmin):
    """Admin per il modello Sede."""

    list_display = ('nome', 'indirizzo', 'citta')
    list_filter: ClassVar[list[str]] = ['citta']
    search_fields: ClassVar[list[str]] = ['nome', 'indirizzo', 'citta__name']
    fields = ('nome', 'indirizzo', 'citta')

    def response_add(self, request, obj, post_url_continue=None):
        """Messaggio di successo personalizzato dopo l'aggiunta di una Sede."""
        msg = _("La %(name)s '%(obj)s' è stata creata con successo.") % {
            'name': self.opts.verbose_name,
            'obj': obj,
        }
        self.message_user(request, msg, level=messages.SUCCESS)
        return super().response_add(request, obj, post_url_continue)

    def response_change(self, request, obj):
        """Messaggio di successo personalizzato dopo la modifica di una Sede."""
        msg = _("La %(name)s '%(obj)s' è stata modificata con successo.") % {
            'name': self.opts.verbose_name,
            'obj': obj,
        }
        self.message_user(request, msg, level=messages.SUCCESS)
        return super().response_change(request, obj)
