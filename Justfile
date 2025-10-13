
set shell := ["powershell", "-c"]

default := "menu"

menu:
    @Write-Host "📦  Project commands" -ForegroundColor White
    @Write-Host "────────────────────────────" -ForegroundColor DarkGray
    @Write-Host ""
    @Write-Host "🟢 Django" -ForegroundColor Green
    @Write-Host "  ▶ run             — Start dev server (just run)" -ForegroundColor Gray
    @Write-Host "  ▶ migrate         — Apply migrations (just migrate)" -ForegroundColor Gray
    @Write-Host "  ▶ makemigrations  — Create migrations (just makemigrations)" -ForegroundColor Gray
    @Write-Host "  ▶ createsuperuser — Create admin user interactively (just createsuperuser)" -ForegroundColor Gray
    @Write-Host "  ▶ collectstatic   — Collect static files (just collectstatic)" -ForegroundColor Gray
    @Write-Host ""
    @Write-Host "🗄️ Database" -ForegroundColor Yellow
    @Write-Host "  ▶ (use your local Postgres; see config/.env.template)" -ForegroundColor Gray
    @Write-Host "  ▶ db-create-role    — Create DB role: just db-create-role NAME PASSWORD" -ForegroundColor Gray
    @Write-Host "  ▶ db-grant-createdb — Grant CREATEDB to role: just db-grant-createdb NAME" -ForegroundColor Gray
    @Write-Host "  ▶ db-create         — Create database: just db-create NAME OWNER" -ForegroundColor Gray
    @Write-Host "  ▶ db-drop           — Drop database: just db-drop NAME" -ForegroundColor Gray
    @Write-Host "  ▶ db-psql           — Open psql: just db-psql DBNAME" -ForegroundColor Gray
    @Write-Host ""
    @Write-Host "🧪 Testing" -ForegroundColor Cyan
    @Write-Host "  ▶ test  — Run tests (just test)" -ForegroundColor Gray
    @Write-Host "  ▶ coverage — Generates coverage report (poetry run pytest --cov)" -ForegroundColor Gray
    @Write-Host ""
    @Write-Host "🧹 Linting & Formatting" -ForegroundColor Magenta
    @Write-Host "  ▶ lint   — Run ruff linter (just lint)" -ForegroundColor Gray
    @Write-Host "  ▶ mypy   — Run static type checks (just mypy)" -ForegroundColor Gray
    @Write-Host "  ▶ format — Autoformat with ruff (just format)" -ForegroundColor Gray
    @Write-Host "  ▶ prettier-md — Format Markdown in root/docs (just prettier-md)" -ForegroundColor Gray
    @Write-Host ""
    @Write-Host "📚 Docs" -ForegroundColor Blue
    @Write-Host "  ▶ docs — Build Sphinx docs (just docs)" -ForegroundColor Gray
    @Write-Host ""
    @Write-Host "⚙️ Utilities" -ForegroundColor White
    @Write-Host "  ▶ help — Show simple help (just help)" -ForegroundColor Gray
    @Write-Host ""

# ----------------------
# Database helpers
# ----------------------

# Usage: just db-create-role NAME PASSWORD
db-create-role NAME PASSWORD:
    @
    $psql = (Get-Command psql -ErrorAction SilentlyContinue).Source -or 'C:\\Program Files\\PostgreSQL\\18\\bin\\psql.exe'
    & $psql -U postgres -h ${PG_HOST:-localhost} -p ${PG_PORT:-5432} -c "CREATE ROLE ${NAME} WITH LOGIN PASSWORD '${PASSWORD}' CREATEDB;"

# Usage: just db-grant-createdb NAME
db-grant-createdb NAME:
    @
    $psql = (Get-Command psql -ErrorAction SilentlyContinue).Source -or 'C:\\Program Files\\PostgreSQL\\18\\bin\\psql.exe'
    & $psql -U postgres -h ${PG_HOST:-localhost} -p ${PG_PORT:-5432} -c "ALTER ROLE ${NAME} CREATEDB;"

# Usage: just db-create NAME OWNER
db-create NAME OWNER:
    @
    $psql = (Get-Command psql -ErrorAction SilentlyContinue).Source -or 'C:\\Program Files\\PostgreSQL\\18\\bin\\psql.exe'
    & $psql -U postgres -h ${PG_HOST:-localhost} -p ${PG_PORT:-5432} -c "CREATE DATABASE ${NAME} OWNER ${OWNER};"

# Usage: just db-drop NAME
db-drop NAME:
    @
    $psql = (Get-Command psql -ErrorAction SilentlyContinue).Source -or 'C:\\Program Files\\PostgreSQL\\18\\bin\\psql.exe'
    & $psql -U postgres -h ${PG_HOST:-localhost} -p ${PG_PORT:-5432} -c "DROP DATABASE IF EXISTS ${NAME};"

# Usage: just db-psql DBNAME
db-psql DBNAME:
    @
    $psql = (Get-Command psql -ErrorAction SilentlyContinue).Source -or 'C:\\Program Files\\PostgreSQL\\18\\bin\\psql.exe'
    & $psql -U ${PGUSER:-postgres} -h ${PG_HOST:-localhost} -p ${PG_PORT:-5432} ${DBNAME}

run:
    @poetry run python manage.py runserver 127.0.0.1:8001

migrate:
    @poetry run python manage.py migrate --noinput

makemigrations:
    @poetry run python manage.py makemigrations

createsuperuser:
    @poetry run python manage.py createsuperuser

shell:
    @poetry run python manage.py shell

test:
    @poetry run pytest --maxfail=1 -q

lint:
    @poetry run ruff check .

format:
    @poetry run ruff format .

docs:
    @poetry run sphinx-build -b html docs/ docs/_build/html

help:
    @echo "Targets: run, migrate, makemigrations, createsuperuser, shell, test, lint, format, docs"

# Run pre-commit hooks on all files
pre-commit-all:
    @poetry run pre-commit run --all-files

mypy ARGS='':
    @poetry run mypy server tests {{ARGS}}

prettier-md:
    @pnpm prettier  --write $(Get-ChildItem -Path . -Filter *.md -File | % { $_.FullName }; Get-ChildItem -Path ./docs -Filter *.md -File -Recurse | % { $_.FullName })

# Collect static files for Django
collectstatic:
    @poetry run python manage.py collectstatic --noinput

generate-django-secret:
     @poetry run python -c "from django.utils.crypto import get_random_string; print(get_random_string(50))"
