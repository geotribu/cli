# Installation

Il est possible d'installer le projet de deux façon différentes, en plus de [celle du mode développement](development/setup).

## Pip

### Prérequis

- Python >= 3.10
- Accès réseau sur :
  - le dépôt officiel de paquets Python : <https://pypi.org/>
  - les différents sous-domaines de Geotribu <https://*geotribu.fr>
  - le site des données NTLK <https://www.nltk.org/nltk_data/>

### Installer

```sh
pip install geotribu
```

----

## Docker

:::{note}
L'image est configurée à des fins d'**utilisation** et non à des fins de développement.  
A ce titre l'image ne contient que le code source et le nécessaire pour installer le programme. Donc, il n'y a pas les dossiers `docs`, `tests`, etc.

Si besoin, ajuster le fichier `.dockerignore`.
:::

### Prérequis

- Docker >= 20.10
- dépôt cloné localement

### Builder l'image

```sh
docker build --pull --rm -f "Dockerfile" -t geotribu:latest "."
```

### Exécuter l'image dans un conteneur

Entrer dans le conteneur et exécuter des commandes de façon interactive :

```sh
> docker run --rm -it geotribu:latest
root@55c5de0191ee:/user/app# geotribu --version
0.2.0
```

Exécuter le programme dans le conteneur :

```sh
> docker run --rm geotribu:latest geotribu --version
0.2.0
```
