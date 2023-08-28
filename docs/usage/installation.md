# Installation

Il est possible d'installer le projet de plusieurs façons différentes, en plus de [celle du mode développement](development/setup).

## Utiliser comme exécutable autonome

1. Download the latest release from [GitHub Release](https://github.com/geotribu/cli/releases/latest):
1. Make sure that it's executable (typically on Linux: `chmod u+x ./GeotribuToolbelt_XXXXXX`)
1. Run it from your favorite shell if you like the CLI - see [the relevant section](/usage/examples)

:::{warning}
MacOS version is not tested and is just here to encourage beta-testing and feedback to improve it.
:::

----

## Utiliser comme package Python

### Prérequis

- Python >= 3.10
- Accès réseau sur :
  - le dépôt officiel de paquets Python : <https://pypi.org/>
  - les différents sous-domaines de Geotribu <https://*geotribu.fr>
  - le site des données NTLK <https://www.nltk.org/nltk_data/>

### Installer

```sh
pip install --upgrade geotribu
```

L'outil est désormais disponible en ligne de commande. Voir les [exemples](/usage/examples).

----

## Avec Docker

Le paquet est publié sous forme d'image Docker dans le registre du dépôt GitHub (GHCR):

```sh
docker pull ghcr.io/geotribu/cli
```

Voir [la page dédié pour plus d'options](https://github.com/geotribu/cli/pkgs/container/cli).
