# {{ title }} - Documentation

> **Description:** {{ description }}  
> **Auteur et contributeurs :** {{ author }}  
> **Version actuelle :** {{ version }}  
> **Code source :** {{ repo_url }}  
> **Date de génération de la documentation :** {{ date_update }}

{{ cli_usage }}

Présentation en vidéo :

<iframe width="100%" height="400" src="https://www.youtube.com/embed/eWNBpUVYakY?si=A5BXKx9ff1NeQfBC" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

---

```{toctree}
---
caption: Usage
maxdepth: 1
---
usage/installation
usage/cli
usage/examples
usage/configuration
```

```{toctree}
---
caption: Développement
maxdepth: 1
---
development/setup
development/contribute
development/documentation
development/testing
development/packaging
development/releasing
development/history
Code documentation <_apidoc/modules>
```

```{toctree}
---
caption: Divers
maxdepth: 1
---
misc/credits
misc/geotribot_manifest.md
Site Geotribu <http://geotribu.fr>
Article d'introduction <https://geotribu.fr/articles/2023/2023-08-25_geotribu-cli-en-ligne-de-commande/>
```
