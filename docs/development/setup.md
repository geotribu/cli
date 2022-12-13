# Configurer l'environnement de développement

## Prérequis système

- Python >= 3.9
- Accès réseau sur :
  - l'instance GitLab : <https://gitlab.gpf-tech.ign.fr>
  - le dépôt officiel de paquets Python : <https://pypi.org/>
- un [jeton d'accès personnel ou Personal Access Token (PAT)](https://gitlab.gpf-tech.ign.fr/-/profile/personal_access_tokens) avec le scope `read_api`

## Cloner le dépôt

Exemple pour Oslandia avec l'utilisateur `geojulien` :

```sh
git clone --config 'credential.helper=store' https://geojulien@gitlab.gpf-tech.ign.fr/geoplateforme/scripts-verification/check-md5.git
```

### Derrière le proxy

L'Usine Logicielle étant en accès restreint derrière un filtre IP, les personnes ne disposant pas d'IP fixe passent par un proxy qui pointe sur un serveur de rebond dont l'IP fixe est autorisée.

Exemple avec un proxy de type socks :

```sh
git clone --config http.proxy='socks5://127.0.0.1:8645' --config 'credential.helper=store' https://geojulien@gitlab.gpf-tech.ign.fr/geoplateforme/scripts-verification/check-md5.git
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
