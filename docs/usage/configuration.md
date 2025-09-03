# Configuration

## Autocomplétion des commandes

L'autocomplétion des commandes est supportée pour les shells `bash` et `zsh` si le paquet Python `argcomplete` est installé.
Pour l'activer, il faut ajouter la ligne suivante dans le fichier de configuration du shell (ex: `~/.bashrc` ou `~/.zshrc`):

```bash
eval "$(register-python-argcomplete geotribu)"
```

## Variables d'environnement supportées

| Nom de la variable  | Description | Option CLI correspondante | Valeur par défaut |
| :------------------ | :---------- | :-----------------------: | :---------------: |
| `GEOTRIBU_AUTO_OPEN_AFTER` | Activer/désactiver l'ouverture automatique du contenu publié à la fin d'une commande de publication (commentaire...). | `--no-auto-open` | `True` |
| `GEOTRIBU_COMMENTS_EXPIRATION_HOURS` | Nombre d'heures à partir duquel considérer le fichier local comme périmé. | `--expiration-rotating-hours` de `comments`  | `4` (1 jour) |
| `GEOTRIBU_COMMENTS_API_PAGE_SIZE` | Nombre de commentaires par requêtes. Plus le commentaire est récent, plus c'est performant d'utiliser une petite page. À l'inverse, si on cherche un vieux commentaire, utiliser une grande page | `--page-size` de `comments` | 20 |
| `GEOTRIBU_CONTENUS_DATE_END` | Date de publication la plus récente sur laquelle filtrer les contenus (format: AAAA-MM-JJ). | `--date-end` de `search-content`  | date du jour |
| `GEOTRIBU_CONTENUS_DATE_START` | Date de publication la plus ancienne sur laquelle filtrer les contenus (format: AAAA-MM-JJ). | `--date-start` de `search-content`  | `2020-01-01` |
| `GEOTRIBU_CONTENUS_DEFAULT_TYPE` | Type de contenu sur lequel filtrer. | `--filter-type` de `search-images`  | `None` |
| `GEOTRIBU_CONTENUS_INDEX_EXPIRATION_HOURS` | Nombre d'heures à partir duquel considérer le fichier local comme périmé. | `--expiration-rotating-hours` de `search-content`  | `24*7` (1 semaine) |
| `GEOTRIBU_DEFAULT_SUBCOMMAND` | Sous-commande à exécuter par défaut quand on lance le CLI sans argument | | `read-latest` |
| `GEOTRIBU_MERGE_CONTENT_BY_UNIQUE_URL` | Cette option permet de désactiver la fusion des résultats qui partagent la même URL. Si désactivée, plusieurs résultats peuvent concerner le même article.  | `-a` ou `--no-fusion-par-url` de `search-content` | `True` |
| `GEOTRIBU_PROXY_HTTP` | Proxy HTTP/S à utiliser spécifiquement. Par défaut, les paramètres systèmes ou les valeurs de `HTTP_PROXY` et `HTTPS_PROXY` sont utilisés. |   | `None` |
| `GEOTRIBU_IMAGES_DEFAULT_TYPE` | Type d'image sur lequel filtrer. | `--filter-type` de `search-images`  | `None` |
| `GEOTRIBU_IMAGES_INDEX_EXPIRATION_HOURS` | Nombre d'heures à partir duquel considérer le fichier local comme périmé. | `--expiration-rotating-hours` de `search-images`  | `24` (1 jour) |
| `GEOTRIBU_MASTODON_STATUS_VISIBILITY` | Visibilité des statuts postés sur Mastodon. Voir [la doc officielle](https://docs.joinmastodon.org/user/posting/#unlisted). |  | `unlisted` |
| `GEOTRIBU_OPEN_WITH` | Avec quoi ouvrir le contenu. | `--with` de `ouvrir` | `shell` |
| `GEOTRIBU_PROMPT_AFTER_SEARCH` | Activer/désactiver l'invite pour sélectionner une action à la fin d'une commande de recherche. | `--no-prompt` | `True` |
| `GEOTRIBU_RESULTATS_FORMAT` | Format de résultat des commandes de recherche | `--format-output` | `table` |
| `GEOTRIBU_RESULTATS_NOMBRE` | Nombre de résultats des commandes de recherche | `-n`/`--results-number` | `5` |
| `GEOTRIBU_UPGRADE_CHECK_ONLY` | Vérifier seulement s'il y a une nouvelle version sans la télécharger. | `-c`, `--check-only` de `upgrade`   | `False` |
| `GEOTRIBU_UPGRADE_DISPLAY_RELEASE_NOTES` | Afficher/masquer les notes de version quand une nouvelle version est disponible | `-n`, `--dont-show-release-notes` de `upgrade` | `True` |
| `GEOTRIBU_UPGRADE_DOWNLOAD_FOLDER` | (chemin où télécharger la nouvelle version) | `-w`, `--where` de `upgrade` | `./` (current folder) |
| `TINIFY_API_KEY`| clé d'API Tinify (requise pour `images optimize`) |  |  |
