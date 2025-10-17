# Guida per sviluppare su macOS

Questo progetto è stato originariamente sviluppato su Windows ma può essere eseguito anche su macOS/Linux.

## File del progetto

- **`Justfile`** - Versione per macOS/Linux (usa bash/zsh)
- **`Justfile.windows`** - Versione originale per Windows (usa PowerShell)

## Setup iniziale su macOS

### 1. Prerequisiti

```bash
# Installare Homebrew (se non già installato)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Installare Python 3.12
brew install python@3.12

# Installare PostgreSQL
brew install postgresql@16

# Avviare PostgreSQL
brew services start postgresql@16

# Installare Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Installare Just
brew install just
```

### 2. Setup del progetto

```bash
# Clonare il repository (se necessario)
cd /percorso/del/progetto

# Configurare Poetry per usare Python 3.12
poetry env use /opt/homebrew/bin/python3.12

# Installare le dipendenze
poetry install

# Creare il database di sviluppo
just db-setup

# Copiare il file di configurazione
cp config/.env.template config/.env

# Modificare config/.env con le credenziali corrette:
# DJANGO_DATABASE_USER=pareri
# DJANGO_DATABASE_PASSWORD=pareri
# DJANGO_DATABASE_NAME=pareri
# DJANGO_DATABASE_HOST=localhost
# DJANGO_DATABASE_PORT=5432

# Eseguire le migrazioni
just migrate

# Creare un superuser
just createsuperuser

# Avviare il server
just run
```

## Comandi principali con Just

```bash
# Vedere tutti i comandi disponibili
just

# Avviare il server di sviluppo
just run

# Eseguire le migrazioni
just migrate

# Creare nuove migrazioni
just makemigrations

# Aprire la shell Django
just shell

# Eseguire i test
just test

# Eseguire il linting
just lint

# Formattare il codice
just format

# Eseguire mypy (type checking)
just mypy

# Generare documentazione
just docs

# Generare una nuova secret key per Django
just generate-django-secret
```

## Comandi database

```bash
# Setup completo del database di sviluppo
just db-setup

# Creare un nuovo ruolo/utente
just db-create-role NOME PASSWORD

# Creare un nuovo database
just db-create NOME_DB PROPRIETARIO

# Aprire psql
just db-psql pareri

# Eliminare un database
just db-drop NOME_DB
```

## Differenze tra Windows e macOS

### Shell
- **Windows**: PowerShell con sintassi `$variable`, `Write-Host`
- **macOS/Linux**: Bash/Zsh con sintassi `$variable`, `echo`

### PostgreSQL
- **Windows**: Solitamente in `C:\Program Files\PostgreSQL\XX\bin\`
- **macOS**: Installato via Homebrew in `/opt/homebrew/bin/` o `/usr/local/bin/`

### Path separators
- **Windows**: `\` (backslash)
- **macOS/Linux**: `/` (forward slash)

### Utente PostgreSQL di default
- **Windows**: Solitamente `postgres`
- **macOS**: L'utente corrente del sistema (ottenibile con `whoami`)

## Troubleshooting

### Poetry non trova Python 3.12
```bash
# Verificare dove si trova Python 3.12
which python3.12

# Configurare Poetry con il path completo
poetry env use /opt/homebrew/bin/python3.12
```

### PostgreSQL non si connette
```bash
# Verificare che PostgreSQL sia in esecuzione
brew services list | grep postgresql

# Avviare PostgreSQL se non è in esecuzione
brew services start postgresql@16

# Verificare la connessione
psql -U $(whoami) -d postgres -c "SELECT version();"
```

### Errore di permessi sul database
```bash
# Ricreare l'utente con i permessi corretti
psql -U $(whoami) -d postgres -c "DROP USER IF EXISTS pareri;"
psql -U $(whoami) -d postgres -c "DROP DATABASE IF EXISTS pareri;"
just db-setup
```

## Ritornare su Windows

Per ritornare a sviluppare su Windows:

```bash
# Salvare il Justfile corrente (se hai fatto modifiche)
cp Justfile Justfile.macos

# Ripristinare la versione Windows
cp Justfile.windows Justfile
```

## Riferimenti

- [Just Command Runner](https://github.com/casey/just)
- [Poetry Documentation](https://python-poetry.org/docs/)
- [PostgreSQL on macOS](https://formulae.brew.sh/formula/postgresql@16)
- [Django Documentation](https://docs.djangoproject.com/)
