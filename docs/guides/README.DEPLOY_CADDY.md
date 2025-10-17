# Deploy Django Admin con Caddy su Windows Server

Questa guida ti aiuta a pubblicare l'interfaccia admin Django su intranet, accessibile da http://`ip-server`/pareri, usando Caddy come reverse proxy e gestore file statici.

## Prerequisiti

- Windows Server 2025
- Python, Django, pip installati
- App Django funzionante (admin attivo)
- Cartella statici generata con `python manage.py collectstatic`

## Step 1: Installa Caddy con Scoop

1. Installa [Scoop](https://scoop.sh/) se non lo hai già:

   ```powershell
   iwr -useb get.scoop.sh | iex
   ```

2. Installa Caddy:

   ```powershell
   scoop install caddy
   ```

3. (Opzionale) Installa nssm per gestire Caddy come servizio:

   ```powershell
   scoop install nssm
   ```

4. Caddy sarà disponibile in `C:\Users\<utente>\scoop\apps\caddy\current\caddy.exe` oppure direttamente nel PATH.

## Step 1b: Configura Caddy come servizio Windows

1. Genera il tuo `Caddyfile` con lo script (vedi sezione sotto) oppure crealo a mano.

2. Copia manualmente il file `Caddyfile` nella cartella di configurazione di Caddy, ad esempio:
   - `<percorso_caddy>\Caddyfile`
   - oppure nella stessa cartella dove lanci il comando `caddy run --config <percorso_caddy>\Caddyfile`

3. Registra Caddy come servizio usando nssm (**PowerShell come amministratore**):

   ```powershell
   nssm install Caddy "caddy" "run" "--config" "<percorso_caddy>\Caddyfile"
   ```

4. Avvia il servizio:

   ```powershell
   nssm start Caddy
   ```

5. Per fermare o riavviare:

   ```powershell
   nssm stop Caddy
   nssm restart Caddy
   ```

6. Il servizio partirà automaticamente all'avvio di Windows.

## Verifica stato dei servizi

Per controllare se Caddy è attivo come servizio Windows:

```powershell
Get-Service Caddy
```

Se lo stato è "Running", il servizio è attivo. Se è "Stopped", puoi avviarlo con:

```powershell
nssm start Caddy
```

Puoi anche usare:

```powershell
sc query Caddy
```

## Step 2: Prepara la cartella statici

1. Esegui:

   ```powershell
   python manage.py collectstatic --noinput
   ```

2. Verifica che la cartella (es: `<percorso_produzione>\pareri\static`) contenga i file statici.

## Step 3: Configura Caddyfile

Crea il file `Caddyfile` in `<percorso_caddy>` con questo contenuto:

```caddyfile
http://<ip-server>/pareri {
   reverse_proxy localhost:8000
   handle_path /static/* {
      root * <percorso_produzione>/pareri/static
      file_server
   }
}
```

Sostituisci `<ip-server>` con l'IP del server.

## Step 4: Avvia Django in produzione

Esempio con Uvicorn:

```powershell
uvicorn server.asgi:application --host 127.0.0.1 --port 8000 --workers 4 --env-file .env.production
```

## Nota su Uvicorn e variabili d'ambiente

Se vuoi usare l'opzione `--env-file` con Uvicorn per caricare automaticamente le variabili dal file `.env`, devi installare la libreria `python-dotenv` nella virtualenv:

```powershell
E:/progetti/pareri/.venv/Scripts/pip.exe install python-dotenv
```

Così Uvicorn caricherà correttamente tutte le variabili definite nel file `.env`.

Se non installi `python-dotenv`, Uvicorn mostrerà l'errore `ModuleNotFoundError: No module named 'dotenv'` e non caricherà le variabili.

Se usi solo `python-decouple` nei settings, le variabili vengono caricate da Django, ma non sono disponibili come variabili d'ambiente per il processo Python/Uvicorn.

## Errori comuni con nssm/Uvicorn

### Errore: `ModuleNotFoundError: No module named 'server'`

Questo errore nei log del servizio Uvicorn avviato con nssm indica che il modulo `server` non viene trovato. Le cause più comuni sono:

- **Startup directory errata**: nssm deve avviare il servizio con la "Startup directory" impostata su `E:\progetti\pareri` (la root del progetto, dove si trova la cartella `server`). Se la directory è diversa, Python non trova il modulo.
- **Percorso python.exe**: Usa il python della virtualenv: `E:\progetti\pareri\.venv\Scripts\python.exe`
- **Arguments corretti**: `-m uvicorn server.asgi:application --host 127.0.0.1 --port 8000` (senza `--workers` su Windows!)
- **Struttura progetto**: La cartella `server` deve essere nella root del progetto:

  ```markdown
  E:\progetti\pareri
  ├── server
  │ └── asgi.py
  ```

**Soluzione:**

1. Apri nssm e controlla che la Startup directory sia `E:\progetti\pareri`.
2. Aggiorna gli Arguments togliendo `--workers`.
3. Riavvia il servizio.

---

Altri errori frequenti:

- **Porta occupata**: Assicurati che la porta 8000 sia libera (`Get-Process -Name python`).
- **Permessi**: Avvia nssm e i servizi come amministratore.
- **Variabili ambiente**: Se usi `.env.production`, aggiungi `--env-file .env.production` agli Arguments.

Consulta questa sezione se il servizio non parte o trovi errori nei log.

## Limitazioni Uvicorn su Windows

Su Windows, Uvicorn non supporta la modalità multiprocess (`--workers > 1`). Se provi ad avviare Uvicorn con più worker, otterrai errori come:

```powershell
OSError: [WinError 10022] Argomento fornito non valido
```

**Best practice:**

- Avvia Uvicorn senza l'opzione `--workers` (default: singolo processo):

  ```pwsh
  E:\progetti\pareri\.venv\Scripts\python.exe -m uvicorn server.asgi:application --host 127.0.0.1 --port 8000
  ```

- Se serve scalabilità, puoi avviare manualmente più istanze Uvicorn su porte diverse e configurare Caddy come reverse proxy/bilanciatore (round-robin).

- L'avviso `ASGI 'lifespan' protocol appears unsupported` è normale con Django e non è un errore.

- Assicurati che la porta scelta sia libera e che non ci siano processi Uvicorn/Django appesi:

  ```pwsh
  Get-Process -Name python
  ```

  Termina eventuali processi appesi con:

  ```pwsh
  Stop-Process -Name python -Force
  ```

Per ambienti Linux, l'opzione `--workers` è supportata e consigliata per produzione.

## Step 5: Avvia Caddy

Apri PowerShell come amministratore e lancia:

```powershell
cd <percorso_caddy>
./caddy run
```

## Step 6: Testa l'accesso

Apri il browser su http://`ip-server`/pareri
Dovresti vedere l'admin Django con i file statici serviti correttamente.

## Genera automaticamente il Caddyfile

Per generare il Caddyfile con la configurazione corretta, usa lo script PowerShell incluso:

1. Apri PowerShell.
2. Esegui lo script:

   ```powershell
   cd <percorso_produzione>\pareri\scripts
   ./create_caddyfile.ps1
   ```

3. Inserisci l'IP del server quando richiesto.
4. Il file verrà creato in `<percorso_produzione>\pareri\scripts\Caddyfile`.

Copialo manualmente nella cartella di configurazione di Caddy, ad esempio:
`<percorso_caddy>\Caddyfile`
Poi lancia Caddy come servizio come descritto sopra.

## Step 7: Installa e avvia Uvicorn come servizio

## Avvio Uvicorn come servizio (consigliato)

Per la produzione, usa nssm per avviare Uvicorn come servizio Windows. Non usare poetry direttamente: usa il python della tua virtualenv.

1. Trova il percorso di python.exe della tua venv (esempio):
   `<percorso_produzione>\pareri\.venv\Scripts\python.exe`

2. Configura nssm:
   - **Application**: `<percorso_produzione>\pareri\.venv\Scripts\python.exe`
   - **Arguments**: `-m uvicorn server.asgi:application --host 127.0.0.1 --port 8000 --workers 4`
   - **Startup directory**: `<percorso_produzione>\pareri`

3. Rimuovi il vecchio servizio (se esiste):

   ```powershell
   nssm remove Uvicorn confirm
   ```

4. Crea il nuovo servizio con nssm (PowerShell come amministratore):

   ```powershell
   nssm install Uvicorn "<percorso_produzione>\pareri\.venv\Scripts\python.exe" "-m uvicorn server.asgi:application --host 127.0.0.1 --port 8000 --workers 4"
   ```

5. Avvia, ferma o riavvia il servizio con:

   ```powershell
   nssm start Uvicorn
   nssm stop Uvicorn
   nssm restart Uvicorn
   ```

## Cambiare nome al servizio Uvicorn

Se vuoi che il servizio Uvicorn abbia un nome personalizzato (es. "Uvicorn Pareri"), rimuovi prima il servizio esistente e poi crealo con il nuovo nome:

```powershell
nssm remove Uvicorn confirm
nssm install "Uvicorn Pareri" "<percorso_venv>\Scripts\python.exe" "-m uvicorn server.asgi:application --host 127.0.0.1 --port 8000 --workers 4"
```

## Configurazione del file .env per la produzione

Per evitare errori come "Invalid HTTP_HOST header" e gestire correttamente i settings di Django in produzione, crea un file `.env.production` nella root del progetto con almeno queste variabili:

```python
DJANGO_SECRET_KEY=... # chiave segreta
DJANGO_ALLOWED_HOSTS=192.168.1.18,localhost
DJANGO_DATABASE_HOST=... # host del database
DJANGO_DATABASE_PORT=... # porta del database
POSTGRES_DB=... # nome db
POSTGRES_USER=... # utente db
POSTGRES_PASSWORD=... # password db
```

Assicurati che Uvicorn venga avviato con l'opzione:

```powershell
--env-file .env.production
```

Così Django userà i settings corretti per la produzione e accetterà le richieste dal reverse proxy Caddy.

## Nota su Caddy nel PATH

## Configurazione corretta Caddy + Django admin su /pareri

## Nota su HTTP, HTTPS e cache browser in intranet

## Cookie CSRF e ambiente intranet (solo HTTP)

Se usi Django in produzione su intranet senza HTTPS, devi impostare:

```python
CSRF_COOKIE_SECURE = False
```

Nei settings di produzione (`production.py`).

Se lasci `CSRF_COOKIE_SECURE = True`, il cookie CSRF verrà inviato solo su HTTPS e il login/admin non funzionerà (errore 403 CSRF verification failed, nessun cookie ricevuto dal browser).

Questa impostazione è sicura in ambiente ufficio/intranet, dove il traffico non passa su Internet.

Se il browser forza il redirect da HTTP a HTTPS anche se Caddy e Django sono configurati solo per HTTP, il problema può essere causato dalla cache HSTS del browser (memorizzata da precedenti visite in HTTPS).

**Soluzioni:**

- Prova ad accedere al sito in una finestra anonima o svuota la cache/HSTS del browser.
- Assicurati che nei settings di produzione Django sia presente:

  ```python
  SECURE_SSL_REDIRECT = False
  ```

- Nel Caddyfile usa solo la direttiva `http://` e nessuna configurazione TLS.

In ambiente ufficio/intranet, puoi tranquillamente usare solo HTTP senza HTTPS.

Per servire l'admin Django direttamente su `/pareri` con i file statici funzionanti:

### 1. Django URLs

Nel file `server/urls.py` mappa l'admin su `/pareri/`:

```python
urlpatterns = [
   path('pareri/', admin.site.urls),
   # ...altre url...
]
```

### 2. Caddyfile

Configura Caddy per inoltrare tutte le richieste `/pareri` e `/pareri/*` a Uvicorn, e servire i file statici:

```caddyfile
http://<ip-server> {
   handle /pareri/static/* {
      root * E:/progetti/pareri/server/staticfiles
      file_server
   }
   handle /pareri* {
      reverse_proxy 127.0.0.1:8000
   }
   log {
      output stdout
      format console
   }
}
```

**Note importanti:**

- Usa `handle /pareri*` (senza path) per gestire sia `/pareri` che `/pareri/qualcosa`.
- Non usare `handle_path` per il reverse proxy, altrimenti Django riceve path errati e i redirect non funzionano.
- I file statici devono essere raccolti in `server/staticfiles`.
- Dopo il login, l'admin sarà sempre su `/pareri`.

### 3. Script PowerShell

Lo script per generare il Caddyfile deve chiedere sia l'IP che la directory del clone, e generare la regola `handle /pareri*`.

Esempio:

```powershell
$ip_server = Read-Host "Inserisci l'IP del server (es: 192.168.1.10)"
$clone_dir = Read-Host "Inserisci la directory dove hai clonato il progetto (es: E:/progetti/pareri)"
$static_dir = Join-Path $clone_dir "server/staticfiles"
$caddyfile_path = Join-Path $PSScriptRoot "Caddyfile"

$caddyfile_content = @"
http://$ip_server {
   handle /pareri/static/* {
      root * $static_dir
      file_server
   }
   handle /pareri* {
      reverse_proxy 127.0.0.1:8000
   }
   log {
      output stdout
      format console
   }
}
"@

Set-Content -Path $caddyfile_path -Value $caddyfile_content -Encoding UTF8
Write-Host "Caddyfile generato in $caddyfile_path con root static: $static_dir"
```

---

Questa configurazione garantisce che l'admin Django sia raggiungibile su `/pareri` e che i file statici siano serviti correttamente.

Se hai installato Caddy con scoop, il comando "caddy" è disponibile tramite la cartella shims di scoop:
`<percorso_scoop>\shims\caddy.exe`
Se non lo trovi, aggiungi questa cartella al PATH dalle variabili d'ambiente di Windows.

> **Nota:** Se usi solo il nome `caddy` come comando, assicurati che la cartella scoop/shims (`<percorso_scoop>\shims`) sia inclusa nel PATH delle variabili d'ambiente del servizio nssm. In alternativa, usa il percorso completo di `caddy.exe` come Application.

Aggiorna questo README man mano che aggiungi step o personalizzazioni.

> **Nota:** Per avviare, fermare o gestire servizi con nssm, apri sempre PowerShell come amministratore.

I servizi configurati con nssm (come Caddy e Uvicorn) sono impostati per avviarsi automaticamente all'avvio di Windows, salvo modifiche manuali.
