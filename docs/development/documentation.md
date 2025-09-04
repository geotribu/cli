# Documentation

Le projet utilise Sphinx pour générer de la documentation à partir de docstrings (documentation en code) et de pages personnalisées écrites en Markdown (via [MyST parser](https://myst-parser.readthedocs.io/en/latest/)).

## Générer le site web de documentation

### Installer les dépendances

```sh
python -m pip install -e .[doc]
```

### Générer les pages spéciales

#### Exemples des commandes

```sh
export GEOTRIBU_PROMPT_AFTER_SEARCH=false
geotribu comments latest --results-number 5 > docs/usage/cli_sample_comments_latest.txt
geotribu rss --format-output table --results-number 3 > docs/usage/cli_sample_rss.txt
geotribu rss -f rdp -o table > docs/usage/cli_sample_rss_rdp.txt
geotribu sc orfeo > docs/usage/cli_sample_search_content_orfeo.txt
geotribu sc -n 10 "+title:openstreetmap postgis" > docs/usage/cli_sample_search_content_advanced.txt
geotribu search-image postgis > docs/usage/cli_sample_search_images_postgis.txt
geotribu search-image postgis -f logo -o json > docs/usage/cli_sample_search_images_postgis_logos_json.txt
```

#### Diagramme des dépendances

```sh
python -m pip install -U "pipdeptree<3"
echo -e "\`\`\`{mermaid}" > docs/misc/dependencies.md
pipdeptree --exclude pip,pipdeptree,setuptools,wheel --mermaid >> docs/misc/dependencies.md
echo -e "    lunr -- "any" --> nltk" >> docs/misc/dependencies.md
echo -e "\`\`\`" >> docs/misc/dependencies.md
```

#### Table des licences

```sh
python -m pip install -U "pip-licenses<5"
pip-licenses --format=markdown --with-authors --with-description --with-urls --ignore-packages geotribu,pipdeptree --output-file=docs/misc/licenses.md
```

### Générer le site

```sh
sphinx-build -b html docs docs/_build/html
```

Ou avec des options d'optimisatoin (silencieux, multiprocessing, doctrees séparés) :

```sh
sphinx-build -b html -d docs/_build/cache -j auto -q docs docs/_build/html
```

Ouvrir `docs/_build/index.html` dans un navigateur web.

----

## Ecrire la documentation en utilisant le rendu instantané

Idéal pour la rédaction locale.

```sh
sphinx-autobuild -b html docs/ docs/_build
```

Ouvrez <http://localhost:8000> dans un navigateur web pour voir le rendu HTML mis à jour lorsqu'un fichier est enregistré.

## Déployer le site web de documentation

Documentation website is hosted on GitLab Pages for every commit pushed on main branch.
