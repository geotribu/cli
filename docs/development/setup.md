# Configurer l'environnement de développement

## Prérequis système

- Python >= 3.10
- Accès réseau sur :
  - le dépôt officiel de paquets Python : <https://pypi.org/>

## Cloner le dépôt

Exemple pour Oslandia avec l'utilisateur `geojulien` :

```sh
git clone https://github.com/geotribu/cli.git
```

## Démarrage rapide

Exemple sur une distribution Linux de type Ubuntu LTS :

```sh
# environnement virtuel
python3 -m venv .venv
source .venv/bin/activate
# mise à jour de pip dans l'environnement virtuel
python -m pip install -U pip setuptools wheel
# installation des dépendances de base
python -m pip install -U -r requirements.txt
# installation du projet en mode développement
python -m pip install -e .
```
