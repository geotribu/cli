# Exemples

## Rerchercher une image

### Recherche simple

```sh
> geotribu search-image postgis
[
    {'nom': 'postgis_db.png', 'dimensions': '400x79', 'score': '9.47', 'url': 'https://cdn.geotribu.fr/img/articles-blog-rdp/serveur/giscloud/postgis_db.png'},
    {
        'nom': 'qgis_postgis_EP.png',
        'dimensions': '790x454',
        'score': '9.47',
        'url': 'https://cdn.geotribu.fr/img/articles-blog-rdp/articles/qgis_postgis_eclairage_public/qgis_postgis_EP.png'
    },
    {
        'nom': 'qgis_postgis_osm_listing.webp',
        'dimensions': '799x390',
        'score': '9.47',
        'url': 'https://cdn.geotribu.fr/img/articles-blog-rdp/articles/postgis_osm_setup/qgis_postgis_osm_listing.webp'
    },
[...]
```

### Filtrer sur un type

```sh
❯ geotribu search-image postgis --filter-type logo
[
    {'nom': 'postgis.png', 'dimensions': '74x74', 'score': '0.934', 'url': 'https://cdn.geotribu.fr/img/logos-icones/logiciels_librairies/postgis.png'},
    {'nom': 'postgis.jpg', 'dimensions': '74x74', 'score': '0.934', 'url': 'https://cdn.geotribu.fr/img/logos-icones/logiciels_librairies/postgis.jpg'},
    {'nom': 'clock-postgis.png', 'dimensions': '400x246', 'score': '0.809', 'url': 'https://cdn.geotribu.fr/img/logos-icones/logiciels_librairies/clock-postgis.png'}
]
```

### Sortie sous forme de tableau

```bash
> geotribu search-image --filter-type logo --format-output table postgis
                                               Recherche d'images - Résultats  
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃               Nom ┃ Dimensions ┃ Score ┃                                                                             Url ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│       postgis.png │      74x74 │ 0.934 │       https://cdn.geotribu.fr/img/logos-icones/logiciels_librairies/postgis.png │
├───────────────────┼────────────┼───────┼─────────────────────────────────────────────────────────────────────────────────┤
│       postgis.jpg │      74x74 │ 0.934 │       https://cdn.geotribu.fr/img/logos-icones/logiciels_librairies/postgis.jpg │
├───────────────────┼────────────┼───────┼─────────────────────────────────────────────────────────────────────────────────┤
│ clock-postgis.png │    400x246 │ 0.809 │ https://cdn.geotribu.fr/img/logos-icones/logiciels_librairies/clock-postgis.png │
└───────────────────┴────────────┴───────┴─────────────────────────────────────────────────────────────────────────────────┘
                                                  Geotribu Toolbelt 0.4.0  

```

Sous forme d'images pour se rendre compte des couleurs (Bash, Ubuntu) :

![Geotribu Toolbelt - Recherche d'images filtrée sous forme de tableau](../static/img/search_image_table_logo.png)
