from django import forms
from django.utils.translation import gettext_lazy as _

from server.apps.datoriLavoro.models import DatoreLavoro


class DatoreLavoroForm(forms.ModelForm):
    """Form personalizzato per il modello DatoreLavoro."""

    class Meta:
        model = DatoreLavoro
        exclude = ('sedi',)  # Escludi M2M con through

    def clean(self):
        """Validazione personalizzata per DatoreLavoro."""
        cleaned_data = super().clean()
        # Mantenere la validazione per ragione_sociale, p_iva e codice_fiscale
        ragione_sociale = cleaned_data.get('ragione_sociale')
        p_iva = cleaned_data.get('p_iva')
        codice_fiscale = cleaned_data.get('codice_fiscale')

        if not ragione_sociale and not p_iva and not codice_fiscale:
            raise forms.ValidationError(
                _(
                    'Devi compilare almeno uno dei seguenti campi:'
                    ' Ragione Sociale, Partita IVA/Codice Fiscale '
                    'o Codice Fiscale.'
                )
            )
        return cleaned_data
