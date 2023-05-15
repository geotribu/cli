# Configuration

## Variables d'environnement supportées

| Nom de la variable  | Description | Option CLI correspondante | Valeur par défaut |
| :------------------ | :---------- | :-----------------------: | :---------------: |
| `GEOTRIBU_CONTENUS_INDEX_EXPIRATION_HOURS` | Nombre d'heures à partir duquel considérer le fichier local comme périmé. | `--expiration-rotating-hours` de `search-content`  | `24*7` (1 semaine) |
| `GEOTRIBU_CONTENUS_DEFAULT_TYPE` | Type de contenu sur lequel filtrer. | `--filter-type` de `search-images`  | `None` |
| `GEOTRIBU_DEFAULT_SUBCOMMAND` | Sous-commande à exécuter par défaut quand on lance le CLI sans argument | | `read-latest` |
| `GEOTRIBU_IMAGES_DEFAULT_TYPE` | Type d'image sur lequel filtrer. | `--filter-type` de `search-images`  | `None` |
| `GEOTRIBU_IMAGES_INDEX_EXPIRATION_HOURS` | Nombre d'heures à partir duquel considérer le fichier local comme périmé. | `--expiration-rotating-hours` de `search-images`  | `24` (1 jour) |
| `GEOTRIBU_RESULTATS_FORMAT` | Format de résultat des commandes de recherche | `--format-output` | `table` |
| `GEOTRIBU_UPGRADE_CHECK_ONLY` | Vérifier seulement s'il y a une nouvelle version sans la télécharger. | `-c`, `--check-only` de `upgrade`   | `False` |
| `GEOTRIBU_UPGRADE_DISPLAY_RELEASE_NOTES` | Afficher/masquer les notes de version quand une nouvelle version est disponible | `-n`, `--dont-show-release-notes` de `upgrade` | `True` |
| `GEOTRIBU_UPGRADE_DOWNLOAD_FOLDER` | (chemin où télécharger la nouvelle version) | `-w`, `--where` de `upgrade` | `./` (current folder) |
