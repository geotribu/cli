# Configuration

## Variables d'environnement supportées

| Nom de la variable  | Description | Option CLI correspondante | Valeur par défaut |
| :------------------ | :---------- | :-----------------------: | :---------------: |
| `GEOTRIBU_DEFAULT_SUBCOMMAND` | Sous-commande à exécuter par défaut quand on lance le CLI sans argument | | `read-latest` |
| `GEOTRIBU_UPGRADE_CHECK_ONLY` | Vérifier seulement s'il y a une nouvelle version sans la télécharger. | `-c`, `--check-only` de `upgrade`   | `False` |
| `GEOTRIBU_UPGRADE_DISPLAY_RELEASE_NOTES` | Afficher/masquer les notes de version quand une nouvelle version est disponible | `-n`, `--dont-show-release-notes` de `upgrade` | `True` |
| `GEOTRIBU_UPGRADE_DOWNLOAD_FOLDER` | (chemin où télécharger la nouvelle version) | `-w`, `--where` de `upgrade` | `./` (current folder) |
