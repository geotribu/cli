# Geotribu CLI

Outil en ligne de commande pour les tâches récurrentes du projet Geotribu.

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/geotribu/cli/main.svg)](https://results.pre-commit.ci/latest/github/geotribu/cli/main)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=geotribu_cli&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=geotribu_cli)

[![🎳 Tester](https://github.com/geotribu/cli/actions/workflows/tests.yml/badge.svg)](https://github.com/geotribu/cli/actions/workflows/tests.yml)
[![📦 Build & 🚀 Release](https://github.com/geotribu/cli/actions/workflows/build_release.yml/badge.svg)](https://github.com/geotribu/cli/actions/workflows/build_release.yml)
[![📚 Documentation](https://github.com/geotribu/cli/actions/workflows/documentation.yml/badge.svg)](https://github.com/geotribu/cli/actions/workflows/documentation.yml)
[![codecov](https://codecov.io/gh/geotribu/cli/branch/main/graph/badge.svg?token=YRLQ6OPFRL)](https://codecov.io/gh/geotribu/cli)

[![PyPi version badge](https://badgen.net/pypi/v/geotribu)](https://pypi.org/project/geotribu/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/geotribu)](https://pypi.org/project/geotribu/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/geotribu)](https://pypi.org/project/geotribu/)

## Installer

Avec [pipx](https://pipx.pypa.io/) (recommandé) :

```sh
pipx install geotribu[all]
```

Via _pip_ :

```sh
pip install geotribu
```

Via Docker :

```sh
docker pull ghcr.io/geotribu/cli
```

Via un exécutable pré-compilé : [télécharger pour son système d'exploitation](https://github.com/geotribu/cli/releases/latest).

## Utiliser

Avec une installation avec un gestionnaire de paquets Python (pipx, pip, uv...) :

```sh
geotribu --help
```

Ou avec l'image Docker :

```sh
docker run --rm -it ghcr.io/geotribu/cli:latest --help
```

Pour plus d'informations, [consulter la documentation](https://cli.geotribu.fr/).
