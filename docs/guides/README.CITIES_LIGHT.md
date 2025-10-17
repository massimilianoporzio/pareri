# Django Cities Light - Configurazione e Setup

Questo documento descrive la configurazione di **django-cities-light** per il progetto Pareri, con dati geografici italiani (città, regioni, province).

## 📦 Installazione

Il pacchetto è già incluso in `pyproject.toml`:

```bash
poetry add django-cities-light
```

## ⚙️ Configurazione

### Settings (`server/settings/components/common.py`)

```python
THIRD_PARTY_APPS = [
    # ... altre app ...
    'cities_light',  # Deve essere PRIMA di tailwind
]

# Configurazione django-cities-light
CITIES_LIGHT_TRANSLATION_LANGUAGES = ['it']  # Solo traduzione italiana
CITIES_LIGHT_INCLUDE_COUNTRIES = ['IT']      # Solo Italia
CITIES_LIGHT_CITY_SOURCES = [
    'http://download.geonames.org/export/dump/cities500.zip',
]
CITIES_LIGHT_ENABLE_GEOCODING = True

# Ignora warning per migration auto-nominate di cities-light
DTM_IGNORED_MIGRATIONS = [
    r'cities_light\.0.*auto_.*',
]
```

### Proxy Models (`server/apps/main/models.py`)

Proxy models con nomi italiani per l'admin:

```python
from cities_light.models import City, Country, Region


class CityProxy(City):
    """Proxy model for City with Italian verbose names."""

    class Meta:
        proxy = True
        verbose_name = 'Città'
        verbose_name_plural = 'Città'
        app_label = 'cities_light'


class RegionProxy(Region):
    """Proxy model for Region with Italian verbose names."""

    class Meta:
        proxy = True
        verbose_name = 'Regione/Provincia'
        verbose_name_plural = 'Regioni/Province'
        app_label = 'cities_light'


class CountryProxy(Country):
    """Proxy model for Country with Italian verbose names."""

    class Meta:
        proxy = True
        verbose_name = 'Nazione'
        verbose_name_plural = 'Nazioni'
        app_label = 'cities_light'
```

### Admin Registration (`server/admin.py`)

```python
from server.apps.main.models import CityProxy, CountryProxy, RegionProxy


class RegionFilter(admin.SimpleListFilter):
    """Filtro personalizzato per Regione con label italiano."""

    title = 'Regione'
    parameter_name = 'region'

    def lookups(self, request, model_admin):
        """Restituisce la lista delle regioni disponibili."""
        regions = RegionProxy.objects.all().order_by('name')
        return [(region.id, region.name) for region in regions]

    def queryset(self, request, queryset):
        """Filtra il queryset in base alla regione selezionata."""
        if self.value():
            return queryset.filter(region_id=self.value())
        return queryset


class CityProxyAdmin(admin.ModelAdmin):
    """Admin per le città italiane."""

    list_display = ('name', 'region', 'country')
    list_filter = (RegionFilter,)
    search_fields = ('name', 'alternate_names')
    ordering = ('name',)

    def get_queryset(self, request):
        """Ottimizza la queryset con select_related per evitare N+1."""
        return super().get_queryset(request).select_related('region', 'country')


class RegionProxyAdmin(admin.ModelAdmin):
    """Admin per le regioni italiane."""

    list_display = ('name', 'country')
    search_fields = ('name', 'alternate_names')
    ordering = ('name',)

    def get_queryset(self, request):
        """Ottimizza la queryset con select_related per evitare N+1."""
        return super().get_queryset(request).select_related('country')


class CountryProxyAdmin(admin.ModelAdmin):
    """Admin per i paesi (Italia)."""

    list_display = ('name', 'code2', 'code3')
    search_fields = ('name', 'code2', 'code3')


custom_admin_site.register(CityProxy, CityProxyAdmin)
custom_admin_site.register(RegionProxy, RegionProxyAdmin)
custom_admin_site.register(CountryProxy, CountryProxyAdmin)
```

## 🚀 Setup Iniziale

### 1. Esegui le migrations

```bash
python manage.py migrate
```

### 2. Importa i dati geografici

⚠️ **Attenzione**: Questo processo può richiedere 5-10 minuti e scarica ~25MB di dati.

```bash
python manage.py cities_light
```

Risultato atteso:

- 1 paese (Italia)
- 20 regioni italiane
- ~11,648 città italiane

### 3. Traduci i nomi in italiano

I dati GeoNames sono in inglese. Esegui il comando di traduzione:

```bash
python manage.py translate_italian_regions
```

Questo comando:

- Traduce il paese: `Italy` → `Italia`
- Traduce le 20 regioni: `The Marches` → `Marche`, `Lombardy` → `Lombardia`, ecc.
- Aggiorna i `display_name` di tutte le città

### 4. Verifica l'importazione

Avvia il server:

```bash
python manage.py runserver
```

Vai su `http://127.0.0.1:8000/admin/cities_light/` e controlla:

- ✅ Città: ~11,648 record
- ✅ Regioni/Province: 20 record (con nomi italiani)
- ✅ Nazioni: 1 record (Italia)

## 🔄 Re-importazione (Se Necessario)

Se hai bisogno di re-importare i dati:

```bash
# 1. Cancella i dati esistenti
python manage.py shell
>>> from cities_light.models import City, Region, Country
>>> City.objects.all().delete()
>>> Region.objects.all().delete()
>>> Country.objects.all().delete()
>>> exit()

# 2. Re-importa
python manage.py cities_light --force-all

# 3. Ri-traduci
python manage.py translate_italian_regions
```

## 💻 Setup su Windows

### PowerShell

```powershell
# 1. Attiva l'ambiente virtuale
poetry shell

# 2. Esegui migrations
python manage.py migrate

# 3. Importa dati (può richiedere tempo)
python manage.py cities_light

# 4. Traduci in italiano
python manage.py translate_italian_regions

# 5. Avvia il server
python manage.py runserver
```

### Note per Windows

1. **Encoding UTF-8**: Se hai problemi con caratteri speciali:

   ```powershell
   [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
   ```

2. **Proxy aziendale**:

   ```powershell
   $env:HTTP_PROXY = "http://proxy:port"
   $env:HTTPS_PROXY = "http://proxy:port"
   ```

3. **Timeout download**: Se il download è lento, aumenta il timeout in settings:
   ```python
   CITIES_LIGHT_DOWNLOAD_TIMEOUT = 3600  # 1 ora
   ```

## 📊 Struttura Dati

### Regioni Italiane (20)

Tradotte in italiano:

- Abruzzo
- Basilicata
- Calabria
- Campania
- Emilia-Romagna
- Friuli Venezia Giulia
- Lazio
- Liguria
- Lombardia
- Marche
- Molise
- Piemonte
- Puglia
- Sardegna
- Sicilia
- Toscana
- Trentino-Alto Adige
- Umbria
- Valle d'Aosta
- Veneto

### Città

Circa 11,648 città italiane da GeoNames (popolazione > 500 abitanti).

Ogni città ha:

- `name`: Nome della città
- `display_name`: Nome completo con regione e paese
- `region`: ForeignKey a RegionProxy
- `country`: ForeignKey a CountryProxy
- `alternate_names`: Nomi alternativi
- `latitude`, `longitude`: Coordinate geografiche

## 🔗 Utilizzo nei Model

Per usare le città nei tuoi modelli:

```python
from server.apps.main.models import CityProxy


class Sede(models.Model):
    """Modello per una sede aziendale."""

    nome = models.CharField(max_length=100)
    indirizzo = models.CharField(max_length=255)
    citta = models.ForeignKey(
        CityProxy,
        on_delete=models.PROTECT,  # Non permettere cancellazione città in uso
        verbose_name="Città"
    )

    def __str__(self):
        return f"{self.nome} - {self.citta}"
```

## ⚡ Performance: N+1 Query Prevention

Gli admin usano `select_related()` per evitare problemi di performance:

```python
def get_queryset(self, request):
    """Ottimizza la queryset con select_related per evitare N+1."""
    return super().get_queryset(request).select_related('region', 'country')
```

Questo è **essenziale** quando si mostrano ForeignKey in `list_display` per evitare migliaia di query al database.

## 🎨 Icone Jazzmin

Le icone sono già configurate in `settings/components/common.py`:

```python
JAZZMIN_SETTINGS = {
    "icons": {
        "cities_light.cityProxy": "fas fa-city",
        "cities_light.countryProxy": "fas fa-earth-europe",
        "cities_light.regionProxy": "fas fa-map-marker-alt",
        # ... altre icone ...
    },
}
```

## 📚 Risorse

- [django-cities-light Documentation](https://django-cities-light.readthedocs.io/)
- [GeoNames](https://www.geonames.org/)
- [Management Command Source](server/apps/main/management/commands/translate_italian_regions.py)

## ❓ Troubleshooting

### Problema: Import molto lento

**Soluzione**: È normale, l'import di 11k+ città richiede tempo. Assicurati di avere una buona connessione internet.

### Problema: Nomi in inglese dopo l'import

**Soluzione**: Esegui il comando di traduzione:

```bash
python manage.py translate_italian_regions
```

### Problema: NPlusOneError nell'admin

**Soluzione**: Gli admin devono usare `select_related()` per i campi ForeignKey mostrati in `list_display`. Vedi la sezione "Performance" sopra.

### Problema: Città duplicate

**Soluzione**: È normale, GeoNames può avere città con lo stesso nome in regioni diverse. Usa il `display_name` per distinguerle.

---

**Ultimo aggiornamento**: Ottobre 2025
