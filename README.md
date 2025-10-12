# pareri

pareri

This project was generated with [`wemake-django-template`](https://github.com/wemake-services/wemake-django-template). Current template version is: [105b09d](https://github.com/wemake-services/wemake-django-template/tree/105b09d7ecfb293f8479c7cd9a5ab787254160d0). See what is [updated](https://github.com/wemake-services/wemake-django-template/compare/105b09d7ecfb293f8479c7cd9a5ab787254160d0...master) since then.

[![wemake.services](https://img.shields.io/badge/%20-wemake.services-green.svg?label=%20&logo=data%3Aimage%2Fpng%3Bbase64%2CiVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAABGdBTUEAALGPC%2FxhBQAAAAFzUkdCAK7OHOkAAAAbUExURQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP%2F%2F%2F5TvxDIAAAAIdFJOUwAjRA8xXANAL%2Bv0SAAAADNJREFUGNNjYCAIOJjRBdBFWMkVQeGzcHAwksJnAPPZGOGAASzPzAEHEGVsLExQwE7YswCb7AFZSF3bbAAAAABJRU5ErkJggg%3D%3D)](https://wemake-services.github.io)
[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)

## Prerequisites

You will need:

- `python3.12` (see `pyproject.toml` for exact version), use `pyenv install`
- `postgresql` (see `docker-compose.yml` for exact version)
- Latest `docker`

## Development

When developing locally, we use:

## pnpm & Dependabot best practice

Per aggiornamenti automatici delle dipendenze JS/TS (es. Prettier) con Dependabot:

- Usa sempre pnpm locale (non globale) per gestire le dipendenze del progetto.
- Assicurati che `package.json` e `pnpm-lock.yaml` siano presenti nella root.
- Installa le dipendenze con `pnpm add --save-dev <package>`.
- Dependabot rileverà e aggiornerà automaticamente le dipendenze tramite il lockfile.

Esempio:

```sh
pnpm add --save-dev prettier
```

Questo garantisce aggiornamenti automatici e riproducibilità delle dipendenze JS/TS.
