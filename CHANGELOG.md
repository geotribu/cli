# CHANGELOG

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

For more detailed changes, see the releases section on GitHub: <https://github.com/geotribu/cli/releases/>.

<!--

Unreleased

## {version_tag} - YYYY-DD-mm

### Added

### Changed

### Removed

-->

## 0.9.1 - 2023-01-13

- Hotfix : Corrige l'argument manquant

## 0.9.0 - 2023-01-13

- Fonctionnalité : ajoute le support des proxy HTTP/S by @Guts in <https://github.com/geotribu/cli/pull/29>
- Homogénéise les sous-commandes en ajoutant l'argument nombre de résultats by @Guts in <https://github.com/geotribu/cli/pull/31>
- Fonctionnalité : ajoute un utilitaire pour obtenir et vérifier les dimensions d'une image by @Guts in <https://github.com/geotribu/cli/pull/32>

## 0.8.0 - 2023-01-06

- Fonctionnalité : ajout sous-commande pour consulter les derniers contenus publiés by @Guts in <https://github.com/geotribu/cli/pull/28>
- Documentation: add sitemap and robots.txt for SEO by @Guts in <https://github.com/geotribu/cli/pull/27>

## 0.7.0 - 2023-01-01

- packaging: add MacOS to targetted platform
- increase test coverage

## 0.6.0 - 2022-12-31

- rewrite search-content subcommand by improving both indexation and search
- add format output argument to search-content with 'table' as first available option

## 0.5.0 - 2022-12-28

- add format output argument to search-image with 'table' as first available option

## 0.4.0 - 2022-12-27

- Improve search-content subcommand
- Add utils to check file against time since its creation or modification

## 0.3.0 - 2022-12-21

- Modernized build and publish workflow for PyPi

## 0.2.0 - 2022-12-21

- First published version
- Achieve project structure
- Add 2 subcommands: search-content and search-image

## 0.1.0 - 2022-12-10

- First functional version
- Unit tests and coverage
- Packaging with pip
- Documentation
- Tooling : formatter, guidelines, git-hooks, linter...
