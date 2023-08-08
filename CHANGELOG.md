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

## 0.26.0 - 2023-08-08

### Features and enhancements 🎉

* Ajoute les tests sur les types personnalisés argparse by @Guts in <https://github.com/geotribu/cli/pull/113>

### Other Changes

* Bascule sur la nouvelle URL du site Geotribu by @Guts in <https://github.com/geotribu/cli/pull/116>

## 0.25.0 - 2023-07-04

### Features and enhancements 🎉

* Refactorise le code lié à Mastodon by @Guts in <https://github.com/geotribu/cli/pull/104>
* Ajoute une option 'q' aux prompts pour permettre de quitter sans ctrl+c by @Guts in <https://github.com/geotribu/cli/pull/108>
* Ajoute les filtres par date à la recherche de contenus by @Guts in <https://github.com/geotribu/cli/pull/109>

### Tooling 🔧

* Affine la configuration des git hooks et corrige la compatibilité avec Python 3.9 by @Guts in <https://github.com/geotribu/cli/pull/112>

## 0.24.0 - 2023-06-30

### Features and enhancements 🎉

* Add expiration_rotating_hours option to comments latest by @Guts in <https://github.com/geotribu/cli/pull/102>
* Améliore la gestion des réponses HTTP 40* by @Guts in <https://github.com/geotribu/cli/pull/103>

## 0.23.0 - 2023-06-28

### Features and enhancements 🎉

* Refacto images module by @Guts in <https://github.com/geotribu/cli/pull/98>
* Refactorize RSS subcmd and related model by @Guts in <https://github.com/geotribu/cli/pull/99>
* Refactorize search related modules by @Guts in <https://github.com/geotribu/cli/pull/100>
* Ajoute une sous-commande pour créer un nouvel article by @Guts in <https://github.com/geotribu/cli/pull/101>

## 0.22.0 - 2023-06-26

### Features and enhancements 🎉

* Commentaires --> Mastodon : définit la visibilité par défaut sur `unlisted` by @Guts in <https://github.com/geotribu/cli/pull/92>
* Commentaires --> Mastodon : indique si le commentaire a déjà été posté by @Guts in <https://github.com/geotribu/cli/pull/93>
* Commentaires --> Mastodon : gérer le fil de discussion by @Guts in <https://github.com/geotribu/cli/pull/94>
* Retire l'en-tête des contenus Markdown avant de les afficher dans le terminal by @Guts in <https://github.com/geotribu/cli/pull/96>
* Améliore la structure du code lié aux commentaires by @Guts in <https://github.com/geotribu/cli/pull/97>

### Documentation 📖

* Add Geotribot manifest by @Guts in <https://github.com/geotribu/cli/pull/95>

## 0.21.0 - 2023-06-19

### Features and enhancements 🎉

* Factorise la conversion des commentaires en Markdown by @Guts in <https://github.com/geotribu/cli/pull/90>
* Fonctionnalité : optimisation des images pour la publication by @Guts in <https://github.com/geotribu/cli/pull/91>

### Tooling 🔧

* Améliore le README et le raccourcit le nom des exécutables by @Guts in <https://github.com/geotribu/cli/pull/89>

## 0.20.0 - 2023-06-18

### Features and enhancements 🎉

* Fonctionnalité : publier les derniers commentaires publiés sur Mastodon. by @Guts in <https://github.com/geotribu/cli/pull/87>
* Fonctionnalité : ouvre automatiquement le commentaire en ligne une fois publié by @Guts in <https://github.com/geotribu/cli/pull/88>

## 0.19.2 - 2023-05-30

### Tooling 🔧

* Corrige la publication de l'image Docker et améliore la doc liée by @Guts in <https://github.com/geotribu/cli/pull/84>

## 0.19.1 - 2023-05-30

### Tooling 🔧

* Add release to GitHub Container Registry by @Guts in <https://github.com/geotribu/cli/pull/83>

## 0.19.0 - 2023-05-30

### Features and enhancements 🎉

* Ajoute une commande pour consulter les derniers commentaires by @Guts in <https://github.com/geotribu/cli/pull/81>

## 0.18.0 - 2023-05-26

### Features and enhancements 🎉

* Fonctionnalité : demande automatiquement quel résultat ouvrir juste après une recherche by @Guts in <https://github.com/geotribu/cli/pull/80>

## 0.17.0 - 2023-05-23

### Features and enhancements 🎉

* Fonctionnalité : ajoute une sous-commande pour ouvrir les résultats des commandes précédentes by @Guts in <https://github.com/geotribu/cli/pull/74>
* Refacto : utilise une unique instance de l'objet Console by @Guts in <https://github.com/geotribu/cli/pull/77>
* Amélioration : utilise le nom du contenu distant comme nom du fichier local by @Guts in <https://github.com/geotribu/cli/pull/79>

### Documentation 📖

* Intègre des sorties du CLI générées au moment de la CI by @Guts in <https://github.com/geotribu/cli/pull/78>

### Tooling 🔧

* Ajoute des git hooks pygrep by @Guts in <https://github.com/geotribu/cli/pull/75>

## 0.16.0 - 2023-05-18

### Bugs fixes 🐛

* Corrige le test en enlevant le numéro de version statique by @Guts in <https://github.com/geotribu/cli/pull/68>

### Features and enhancements 🎉

* Meilleurs résultats de la recherche de contenus : ajout du titre cliquable et des mots-clés by @Guts in <https://github.com/geotribu/cli/pull/72>
* Améliore des résultats de la recherche d'images : nom cliquable et rappel terme de recherche by @Guts in <https://github.com/geotribu/cli/pull/71>
* Ajoute l'icône à l'exécutable pour Windows by @Guts in <https://github.com/geotribu/cli/pull/70>

### Documentation 📖

* Documentation : ajoute le graphe des dépendances by @Guts in <https://github.com/geotribu/cli/pull/69>
* Détaille la description et l'usage du CLI by @Guts in <https://github.com/geotribu/cli/pull/73>

## 0.15.0 - 2023-05-16

### Features and enhancements 🎉

* Améliore l'affichage des liens dans le terminal by @Guts in <https://github.com/geotribu/cli/pull/67>

## 0.14.0 - 2023-05-16

### Features and enhancements 🎉

* Ajoute une sous-commande par défaut et la rend paramétrable by @Guts in <https://github.com/geotribu/cli/pull/65>
* Améliore les sous-commandes de recherche : spinner, variables d'environnement, metavars by @Guts in <https://github.com/geotribu/cli/pull/66>

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
