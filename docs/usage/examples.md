# Exemples

:::{note}
Les sorties présentées sur cette page sont générées automatiquement durant la génération de la documentation dans la CI. Elles ne sont donc pas représentatives du rendu sur le terminal de chacun/e.
:::

## Consulter les derniers contenus publiés

### Récupération simple

```sh
geotribu read-latest
```

Sortie :

```{eval-rst}
.. literalinclude:: ./cli_sample_rss.txt
  :language: shell
```

### Dernières GeoRDP sous forme de tableau

```sh
geotribu read-latest -f rdp -o table
```

Sortie :

```{eval-rst}
.. literalinclude:: ./cli_sample_rss_rdp.txt
  :language: shell
```

----

## Rechercher un contenu

### Recherche simple

```sh
geotribu sc orfeo
```

Sortie :

```{eval-rst}
.. literalinclude:: ./cli_sample_search_content_orfeo.txt
  :language: shell
```

### Rechercher avancée : forcer la présence d'un mot dans le titre et afficher jusqu'à 10 résultats

```sh
geotribu sc -n 10 "+title:openstreetmap postgis"
```

Sortie :

```{eval-rst}
.. literalinclude:: ./cli_sample_search_content_advanced.txt
  :language: shell
```

### Filtrer sur un type et présenter sous forme de JSON

```sh
geotribu search-image postgis --filter-type logo
```

Sortie :

```{eval-rst}
.. literalinclude:: ./cli_sample_search_images_postgis_logos_json.txt
  :language: json
```

----

## Rechercher une image

### Recherche simple

```sh
geotribu search-image postgis
```

Sortie :

```{eval-rst}
.. literalinclude:: ./cli_sample_search_images_postgis.txt
  :language: shell
```

Voici une capture d'écran de la sortie pour se rendre compte des couleurs (Bash, Ubuntu) :

![Geotribu Toolbelt - Recherche d'images filtrée sous forme de tableau](../static/img/geotribu_search-image_postgis.png)

### Filtrer sur un type et présenter sous forme de JSON

```sh
geotribu search-image postgis --filter-type logo
```

Sortie :

```{eval-rst}
.. literalinclude:: ./cli_sample_search_images_postgis_logos_json.txt
  :language: json
```

----

## Ouvrir un résultat

Après une commande de recherche, il est possible d'afficher un résultat parmi ceux retournés en utilisant le numéro de ligne (index 0).

```sh
# recherche de contenu
> geotribu sc fme
                                                      Recherche de contenus - 5/61 résultats avec le terme : fme  
                                                           (ctrl+clic sur le titre pour ouvrir le contenu)  
┏━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ # ┃ Titre                                                     ┃  Type   ┃ Date de publication ┃ Score ┃                                                  Mots-clés ┃
┡━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 0 │ Passer les données de bande de FME à GDAL pour créer le   │ Article │    02 août 2022     │ 60.8  │                                     FME,GDAL,Python,raster │
│   │ raster de proximité                                       │         │                     │       │                                                            │
├───┼───────────────────────────────────────────────────────────┼─────────┼─────────────────────┼───────┼────────────────────────────────────────────────────────────┤
│ 1 │ FME World Tour 2020 - Edition Veremes online              │ GeoRDP  │     15 mai 2020     │ 57.8  │                        FME,GDAL,GeoMapFish,GeoServer,GRASS │
│   │                                                           │         │                     │       │                              GIS,OpenStreetMap,Python,QGIS │
├───┼───────────────────────────────────────────────────────────┼─────────┼─────────────────────┼───────┼────────────────────────────────────────────────────────────┤
│ 2 │ API Python de FME : comment travailler avec des rasters   │ Article │    02 août 2022     │ 56.3  │                                     FME,GDAL,Python,raster │
│   │ et GDAL                                                   │         │                     │       │                                                            │
├───┼───────────────────────────────────────────────────────────┼─────────┼─────────────────────┼───────┼────────────────────────────────────────────────────────────┤
│ 3 │ Conférence FME 2021                                       │ GeoRDP  │     21 mai 2021     │ 52.4  │                                             cadastre,carte │
│   │                                                           │         │                     │       │ routière,CloudCompare,ENSG,GraphHopper,IGN,OpenStreetMap,… │
│   │                                                           │         │                     │       │                                                       QGIS │
├───┼───────────────────────────────────────────────────────────┼─────────┼─────────────────────┼───────┼────────────────────────────────────────────────────────────┤
│ 4 │ Nouveau transformer révolutionnaire pour FME : RRIP       │ GeoRDP  │     12 mai 2023     │ 42.2  │ Afigéo,armée,cybersécurité,Discord,écosystème,FME,géomati… │
│   │ (Rename, Remarketing and Increase Prices)                 │         │                     │       │                                                            │
└───┴───────────────────────────────────────────────────────────┴─────────┴─────────────────────┴───────┴────────────────────────────────────────────────────────────┘
                                                                       Geotribu Toolbelt 0.16.0  
> geotribu ouvrir 1
```
