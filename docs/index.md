# {{ title }} - Documentation

> **Description:** {{ description }}  
> **Auteur et contributeurs :** {{ author }}  
> **Version actuelle :** {{ version }}  
> **Code source :** {{ repo_url }}  
> **Date de génération de la documentation :** {{ date_update }}

{{ cli_usage }}

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
Site Geotribu <http://geotribu.fr>
```
