from datoriLavoro.models import DatoreLavoro
from django import forms
from django.utils.translation import gettext_lazy as _


class DatoreLavoroForm(forms.ModelForm):
    """Form personalizzato per il modello DatoreLavoro."""

    class Meta:
        model = DatoreLavoro
        fields = '__all__'

    def clean_sedi(self):
        """Assicura che almeno una sede sia associata al datore di lavoro."""
        sedi = self.cleaned_data.get('sedi')
        if not sedi:
            raise forms.ValidationError(
                _('Devi associare almeno una sede a questo datore di lavoro.')
            )
        return sedi

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
