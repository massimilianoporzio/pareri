# Justfile — common developer tasks for this project
# Requires: just (https://github.com/casey/just)

# Default target
default: menu

# Menu: pretty command list with sections and emoji
menu:
    @echo "📦  Project commands"
    @echo "────────────────────────────"
    @echo ""
    @echo "🟢 Django"
    @echo "  ▶ run             — Start dev server (just run)"
    @echo "  ▶ migrate         — Apply migrations (just migrate)"
    @echo "  ▶ makemigrations  — Create migrations (just makemigrations)"
    @echo "  ▶ createsuperuser — Create admin user interactively (just createsuperuser)"
    @echo "  ▶ collectstatic   — Collect static files (just collectstatic)"
    @echo "  ▶ shell           — Open Django shell (just shell)"
    @echo ""
    @echo "🗄️  Database"
    @echo "  ▶ db-create-role    — Create DB role: just db-create-role NAME PASSWORD"
    @echo "  ▶ db-grant-createdb — Grant CREATEDB to role: just db-grant-createdb NAME"
    @echo "  ▶ db-create         — Create database: just db-create NAME OWNER"
    @echo "  ▶ db-drop           — Drop database: just db-drop NAME"
    @echo "  ▶ db-psql           — Open psql: just db-psql DBNAME"
    @echo "  ▶ db-setup          — Setup dev database (user & db 'pareri')"
    @echo ""
    @echo "🧪 Testing"
    @echo "  ▶ test     — Run tests (just test)"
    @echo "  ▶ coverage — Generate coverage report (just coverage)"
    @echo ""
    @echo "🧹 Linting & Formatting"
    @echo "  ▶ lint   — Run ruff linter (just lint)"
    @echo "  ▶ mypy   — Run static type checks (just mypy)"
    @echo "  ▶ format — Autoformat with ruff (just format)"
    @echo "  ▶ prettier-md — Format Markdown files (just prettier-md)"
    @echo ""
    @echo "📚 Docs"
    @echo "  ▶ docs — Build Sphinx docs (just docs)"
    @echo ""
    @echo "⚙️  Utilities"
    @echo "  ▶ pre-commit-all      — Run pre-commit on all files"
    @echo "  ▶ generate-django-secret — Generate Django secret key"
    @echo "  ▶ help                — Show simple help"
    @echo ""

# ----------------------
# Database helpers
# ----------------------

# Usage: just db-create-role NAME PASSWORD
db-create-role NAME PASSWORD:
    @psql -U $(whoami) -h ${PG_HOST:-localhost} -p ${PG_PORT:-5432} -d postgres -c "CREATE ROLE {{NAME}} WITH LOGIN PASSWORD '{{PASSWORD}}' CREATEDB;"

# Usage: just db-grant-createdb NAME
db-grant-createdb NAME:
    @psql -U $(whoami) -h ${PG_HOST:-localhost} -p ${PG_PORT:-5432} -d postgres -c "ALTER ROLE {{NAME}} CREATEDB;"

# Usage: just db-create NAME OWNER
db-create NAME OWNER:
    @psql -U $(whoami) -h ${PG_HOST:-localhost} -p ${PG_PORT:-5432} -d postgres -c "CREATE DATABASE {{NAME}} OWNER {{OWNER}};"

# Usage: just db-drop NAME
db-drop NAME:
    @psql -U $(whoami) -h ${PG_HOST:-localhost} -p ${PG_PORT:-5432} -d postgres -c "DROP DATABASE IF EXISTS {{NAME}};"

# Usage: just db-psql DBNAME
db-psql DBNAME:
    @psql -U ${PGUSER:-$(whoami)} -h ${PG_HOST:-localhost} -p ${PG_PORT:-5432} {{DBNAME}}

# Setup development database (creates user and database 'pareri')
db-setup:
    @echo "Setting up development database..."
    @psql -U $(whoami) -d postgres -f scripts/create_dev_database.sql
    @echo "✅ Database 'pareri' created with user 'pareri'"

# ----------------------
# Django commands
# ----------------------

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

collectstatic:
    @poetry run python manage.py collectstatic --noinput

# ----------------------
# Testing
# ----------------------

test:
    @poetry run pytest --maxfail=1 -q

coverage:
    @poetry run pytest --cov --cov-report=html --cov-report=term

# ----------------------
# Linting & Formatting
# ----------------------

lint:
    @poetry run ruff check .

format:
    @poetry run ruff format .

mypy ARGS='':
    @poetry run mypy server tests {{ARGS}}

# ----------------------
# Documentation
# ----------------------

docs:
    @poetry run sphinx-build -b html docs/ docs/_build/html

# ----------------------
# Utilities
# ----------------------

help:
    @echo "Available targets:"
    @echo "  run, migrate, makemigrations, createsuperuser, shell, test, lint, format, docs"

pre-commit-all:
    @poetry run pre-commit run --all-files

generate-django-secret:
    @poetry run python -c "from django.utils.crypto import get_random_string; print(get_random_string(50))"

prettier-md:
    @pnpm prettier --write $(find . -maxdepth 1 -type f -name "*.md") $(find ./docs -type f -name "*.md")
