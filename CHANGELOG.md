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

## 0.13.0 - 2023-05-15

### Features and enhancements 🎉

* Upgrade : télécharge la nouvelle version de l'exécutable uniquement dans un contexte d'application packagée by @Guts in <https://github.com/geotribu/cli/pull/63>
* Upgrade : gère le jeton Github en variable d'environnement et ajoute une option pour ne pas afficher les notes de version by @Guts in <https://github.com/geotribu/cli/pull/64>

## 0.12.0 - 2023-05-15

### Features and enhancements 🎉

* Affiche les notes de version dans le terminal quand une nouvelle version est disponibel by @Guts in <https://github.com/geotribu/cli/pull/38>
* Dépendances : remplace SemVer par Packaging by @Guts in <https://github.com/geotribu/cli/pull/59>

### Tooling 🔧

* Outillage : étend les git hooks by @Guts in <https://github.com/geotribu/cli/pull/58>
* CI/CD : déploie la doc uniquement sur les tags by @Guts in <https://github.com/geotribu/cli/pull/62>

### Other Changes

* Corrige les docstrings by @Guts in <https://github.com/geotribu/cli/pull/41>

## 0.11.0 - 2023-01-20

* Ajoute une sous-commande pour vérifier et télécharger la dernière version disponible by @Guts in <https://github.com/geotribu/cli/pull/36>
* RSS : définit le format de sortie par défaut sur tableau by @Guts in <https://github.com/geotribu/cli/pull/37>

## 0.10.0 - 2023-01-14

* Fonctionnalité : ajoute la date aux résultats de la recherche de contenus by @Guts in <https://github.com/geotribu/cli/pull/34>
* Améliore les performances de l'indexation et de la recherche by @Guts in <https://github.com/geotribu/cli/pull/35>
* Elargit la couverture des tests by @Guts in <https://github.com/geotribu/cli/pull/30>

## 0.9.1 - 2023-01-13

* Hotfix : Corrige l'argument manquant

## 0.9.0 - 2023-01-13

* Fonctionnalité : ajoute le support des proxy HTTP/S by @Guts in <https://github.com/geotribu/cli/pull/29>
* Homogénéise les sous-commandes en ajoutant l'argument nombre de résultats by @Guts in <https://github.com/geotribu/cli/pull/31>
* Fonctionnalité : ajoute un utilitaire pour obtenir et vérifier les dimensions d'une image by @Guts in <https://github.com/geotribu/cli/pull/32>

## 0.8.0 - 2023-01-06

* Fonctionnalité : ajout sous-commande pour consulter les derniers contenus publiés by @Guts in <https://github.com/geotribu/cli/pull/28>
* Documentation: add sitemap and robots.txt for SEO by @Guts in <https://github.com/geotribu/cli/pull/27>

## 0.7.0 - 2023-01-01

* packaging: add MacOS to targetted platform
* increase test coverage

## 0.6.0 - 2022-12-31

* rewrite search-content subcommand by improving both indexation and search
* add format output argument to search-content with 'table' as first available option

## 0.5.0 - 2022-12-28

* add format output argument to search-image with 'table' as first available option

## 0.4.0 - 2022-12-27

* Improve search-content subcommand
* Add utils to check file against time since its creation or modification

## 0.3.0 - 2022-12-21

* Modernized build and publish workflow for PyPi

## 0.2.0 - 2022-12-21

* First published version
* Achieve project structure
* Add 2 subcommands: search-content and search-image

## 0.1.0 - 2022-12-10

* First functional version
* Unit tests and coverage
* Packaging with pip
* Documentation
* Tooling : formatter, guidelines, git-hooks, linter...
