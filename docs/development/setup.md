# Configurer l'environnement de développement

## Prérequis système

- Python >= 3.10
- Accès réseau sur :
    - le dépôt officiel de paquets Python : <https://pypi.org/>
    - les sites Geotribu

## Cloner le dépôt

Exemple en utilisant le protocole HTTPS :

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
# installation du projet en mode développement avec toutes les dépendances fonctionnelles
python -m pip install -e .[all,dev,doc,test]
```
