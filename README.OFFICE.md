# Deployment e setup in ufficio (Windows Server)

Questa guida contiene i passi pratici per mettere in produzione/collegare il progetto "pareri" su un server Windows (es. Windows Server 2025) in intranet.

Segui i comandi PowerShell indicati. Adatta i percorsi (`C:\srv\pareri`, `C:\Users\massi\...`) al tuo ambiente.

## Sommario rapido

- Installare Python 3.12
- Installare PostgreSQL (consigliato: installer ufficiale) o usare WSL2
- Creare virtualenv e installare dipendenze (poetry o pip)
- Configurare `config/.env` con i valori di produzione
- Eseguire `migrate`, `collectstatic`, `createsuperuser`
- Avviare l'app come servizio (Waitress + NSSM o servizio nativo)
- Mettere davanti un reverse-proxy (IIS, Caddy o Nginx)

---

## 1) Prerequisiti server

- Python 3.12 installato
- Accesso amministratore per installare servizi e PostgreSQL
- Spazio su disco per `STATIC_ROOT` e `MEDIA_ROOT`

## 2) Installare PostgreSQL (raccomandato: installer ufficiale)

1. Scarica l'installer: https://www.postgresql.org/download/windows/
2. Esegui il setup come Administrator. Durante l'installazione:
   - imposta la password del superuser `postgres`
   - scegli la cartella `data` (default OK)
   - abilita il servizio Windows per l'avvio automatico

Verifica con PowerShell:

```powershell
psql --version
psql -U postgres -h localhost -c "\l"
```

Se preferisci WSL2 (Ubuntu) usare PostgreSQL dentro WSL, i comandi sono quelli standard `apt install postgresql`.

---

## 3) Preparare il progetto (cartella consigliata `C:\srv\pareri`)

Esegui questi comandi come utente che gestirà l'app (non necessariamente Admin):

```powershell
# Clona il repo (se non l'hai già)
cd C:\srv
git clone <tuo-repo> pareri
cd pareri

# Crea virtualenv
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Se usi poetry (raccomandato):
# poetry config virtualenvs.in-project true --local
# poetry install

# Oppure con pip (se hai requirements.txt):
pip install -U pip
pip install -r requirements.txt
```

Nota: non committare `.venv` nel repository. Ricreala sul server con i comandi sopra.

---

## 4) Configurare `config/.env`

Copia il template e modifica i valori (non committare questo file):

```powershell
Copy-Item .\config\.env.template .\config\.env
# poi apri e modifica config\.env con valori di produzione
notepad .\config\.env
```

Valori minimi da impostare:

- DJANGO_SECRET_KEY
- DJANGO_ENV=production
- DOMAIN_NAME
- POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
- DJANGO_DATABASE_HOST (es. indirizzo DB in intranet) e PORT

Generare DJANGO_SECRET_KEY (esempio):

```powershell
.\.venv\Scripts\Activate.ps1
python -c "from django.utils.crypto import get_random_string; print(get_random_string(50))"
```

---

## 5) Creare DB e utente PostgreSQL

Usa `psql` (da server) come `postgres` superuser:

```powershell
psql -U postgres -h localhost -c "CREATE USER pareri WITH PASSWORD 'ReplaceWithStrongPassword';"
psql -U postgres -h localhost -c "CREATE DATABASE pareri OWNER pareri ENCODING 'UTF8' TEMPLATE template0;"
psql -U postgres -h localhost -c "GRANT ALL PRIVILEGES ON DATABASE pareri TO pareri;"
```

Se il server psql richiede password e non la conosci: vedi il file `pg_hba.conf` e la procedura per resettare temporaneamente l'autenticazione (solo in locale e con cautela).

---

## 6) Eseguire migrazioni, createsuperuser, collectstatic

```powershell
.\.venv\Scripts\Activate.ps1
cd C:\srv\pareri
python manage.py migrate --noinput
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

---

## 7) Avviare l'app come servizio Windows

Opzione consigliata su Windows: `waitress` (WSGI) + NSSM per gestire il servizio.

1. Installa waitress nel venv:

```powershell
.\.venv\Scripts\Activate.ps1
pip install waitress
```

2. Comando di avvio per test (non come servizio):

```powershell
.\.venv\Scripts\waitress-serve.exe --listen=127.0.0.1:8000 server.wsgi:application
```

3. Creare un servizio usando NSSM (scarica NSSM e posizionalo in `C:\tools\nssm\nssm.exe`):

```powershell
# installa servizio
C:\tools\nssm\nssm.exe install pareri-app
# nel dialog impostare:
# Path: C:\srv\pareri\.venv\Scripts\waitress-serve.exe
# Arguments: --listen=127.0.0.1:8000 server.wsgi:application
# Startup dir: C:\srv\pareri
# Environment: aggiungi DJANGO_ENV=production se vuoi

# poi avvia
C:\tools\nssm\nssm.exe start pareri-app
```

Alternativa: usare `winsw` o creare un servizio custom. Evita gunicorn su Windows (non supportato).

---

## 8) Reverse proxy e TLS

- Opzioni comuni: IIS+ARR (native Windows), Caddy (semplice, cross-platform), Nginx (meno comune su Windows).
- Per intranet con CA aziendale probabilmente userai IIS; per HTTPS automatico e facile usa Caddy.

Esempio minimale Caddyfile:

```
pareri.intranet.local {
    reverse_proxy 127.0.0.1:8000
    file_server /static/* C:\srv\pareri\static
}
```

Se usi IIS/ARR, configura il reverse proxy verso `127.0.0.1:8000` e configura i certificati tramite la CA aziendale.

---

## 9) Troubleshooting rapido

- Se `psql` dice "password authentication failed": controlla `pg_hba.conf` e il superuser password.
- Se il servizio non parte: controlla permessi sulla cartella `data` e i log di PostgreSQL (Event Viewer o `pg_log`).
- Se venv è tracciato da git: assicurati che `.gitignore` contenga `.venv/` e rimuovi la cartella dall'indice con `git rm -r --cached .venv`.

---

## 10) Checklist finale prima del collaudo

- [ ] `config/.env` presente con valori di produzione
- [ ] DB `pareri` e utente `pareri` creati
- [ ] `python manage.py migrate` completato
- [ ] `python manage.py collectstatic` completato
- [ ] Servizio `pareri-app` installato e in esecuzione
- [ ] Reverse proxy configurato e testato (http/https)

---

Se vuoi, posso:

- generare uno script PowerShell che crea l'utente DB e il database (da eseguire come Admin),
- preparare il file `nssm` o i comandi NSSM già pronti con i path del tuo progetto,
- o creare un `server/settings/environments/production.py` di esempio che imposti `DEBUG=False` e `STATIC_ROOT`/`MEDIA_ROOT` per il server.

Dimmi cosa preferisci che faccia adesso e procedo.
