#! python3

# ############################################################################
# ########## IMPORTS #############
# ################################

# standard library
import argparse
import hashlib
import logging
from collections import defaultdict
from os import getenv
from pathlib import Path

# 3rd party
import orjson
from requests import Session
from rich.table import Table

# package
from geotribu_cli.__about__ import __title__, __version__
from geotribu_cli.console import console
from geotribu_cli.constants import GeotribuDefaults
from geotribu_cli.utils.file_downloader import download_remote_file_to_local
from geotribu_cli.utils.proxies import get_proxy_settings

# ############################################################################
# ########## GLOBALS #############
# ################################

logger = logging.getLogger(__name__)
defaults_settings = GeotribuDefaults()

# ############################################################################
# ########## FUNCTIONS ###########
# ################################


def group_images_by_dimensions(
    images_dict: dict[str, list[int]],
) -> dict[tuple[int, int], list[str]]:
    """Regroupe les chemins d'images par leurs dimensions (largeur, hauteur).

    C'est la première passe de détection : deux images de dimensions identiques
    sont candidates au statut de doublon, mais pas encore confirmées.

    Args:
        images_dict: dictionnaire {chemin_relatif: [largeur, hauteur]} issu de
            l'index de recherche CDN.

    Returns:
        Dictionnaire {(largeur, hauteur): [chemin1, chemin2, ...]} ne contenant
        que les groupes d'au moins deux images.

    Example:

    .. code-block:: python

        >>> images = {
        ...     "logos/qgis.png": [200, 200],
        ...     "logos/qgis_copy.png": [200, 200],
        ...     "articles/carte.png": [800, 600],
        ... }
        >>> groups = group_images_by_dimensions(images)
        >>> print(groups)
        {(200, 200): ["logos/qgis.png", "logos/qgis_copy.png"]}
    """
    groups: dict[tuple[int, int], list[str]] = defaultdict(list)

    for relative_path, dimensions in images_dict.items():
        # L'index stocke les dimensions comme une liste [largeur, hauteur]
        width, height = dimensions[0], dimensions[1]
        groups[(width, height)].append(relative_path)

    # On ne garde que les groupes avec au moins 2 images (candidats doublons)
    return {dims: paths for dims, paths in groups.items() if len(paths) >= 2}


def compute_remote_image_hash(
    image_url: str,
    chunk_size: int = 8192,
) -> str | None:
    """Télécharge une image et calcule son empreinte SHA-256 sans la sauvegarder.

    L'empreinte cryptographique (hash) est une "signature" unique du contenu :
    deux fichiers identiques auront toujours le même hash. C'est la méthode
    la plus fiable pour confirmer un doublon.

    On utilise le streaming pour éviter de charger toute l'image en mémoire :
    on lit par petits morceaux (chunks) et on les intègre progressivement
    au calcul du hash.

    Args:
        image_url: URL complète de l'image à vérifier.
        chunk_size: taille des morceaux lus en octets. Defaults to 8192.

    Returns:
        Empreinte SHA-256 hexadécimale, ou None en cas d'erreur.
    """
    try:
        with Session() as session:
            session.proxies.update(get_proxy_settings())
            session.headers.update({"User-Agent": f"{__title__}/{__version__}"})

            with session.get(image_url, stream=True, timeout=(30, 60)) as response:
                response.raise_for_status()

                sha256 = hashlib.sha256()
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        sha256.update(chunk)

        return sha256.hexdigest()

    except Exception as err:
        logger.warning(
            f"Impossible de calculer l'empreinte de {image_url}. Trace : {err}"
        )
        return None


def find_duplicate_images(
    images_dict: dict[str, list[int]],
    cdn_base_url: str,
    cdn_base_path: str,
    check_content: bool = False,
) -> list[list[str]]:
    """Identifie les images en doublon dans le CDN.

    Algorithme en deux passes :

    1. Groupement par dimensions (rapide, sans téléchargement) pour trouver
       les candidats.
    2. Si check_content=True, téléchargement et comparaison par hash SHA-256
       pour confirmer les vrais doublons (même contenu, pas seulement mêmes
       dimensions).

    Args:
        images_dict: dictionnaire {chemin_relatif: [largeur, hauteur]}.
        cdn_base_url: URL de base du CDN (ex: "https://cdn.geotribu.fr/").
        cdn_base_path: chemin de base des images (ex: "img").
        check_content: si True, vérifie le contenu par hash SHA-256.
            Attention : nécessite de télécharger toutes les images candidates.
            Defaults to False.

    Returns:
        Liste de groupes, chaque groupe étant une liste de chemins relatifs
        d'images identiques.
    """
    # --- Passe 1 : candidats par dimensions ---
    dimension_groups = group_images_by_dimensions(images_dict)

    if not dimension_groups:
        logger.info("Aucun candidat doublon trouvé par dimensions.")
        return []

    logger.info(
        f"{len(dimension_groups)} groupe(s) de candidats doublons "
        f"trouvés par dimensions (représentant "
        f"{sum(len(p) for p in dimension_groups.values())} images)."
    )

    if not check_content:
        # On retourne les candidats sans vérification de contenu
        return list(dimension_groups.values())

    # --- Passe 2 : confirmation par hash SHA-256 ---
    true_duplicates: list[list[str]] = []
    total_candidates = sum(len(paths) for paths in dimension_groups.values())
    processed = 0

    for (width, height), candidate_paths in dimension_groups.items():
        hash_groups: dict[str, list[str]] = defaultdict(list)

        for relative_path in candidate_paths:
            image_url = f"{cdn_base_url}{cdn_base_path}/{relative_path}"
            processed += 1

            with console.status(
                f"Vérification du contenu ({processed}/{total_candidates}) : "
                f"{relative_path}...",
                spinner="dots",
            ):
                file_hash = compute_remote_image_hash(image_url)

            if file_hash:
                hash_groups[file_hash].append(relative_path)
                logger.debug(f"  {relative_path} → SHA-256: {file_hash[:12]}...")

        # Seuls les groupes avec ≥2 images ayant le même hash sont de vrais doublons
        for file_hash, dup_paths in hash_groups.items():
            if len(dup_paths) >= 2:
                true_duplicates.append(dup_paths)
                logger.info(
                    f"Vrai doublon confirmé (hash {file_hash[:12]}...) : "
                    + ", ".join(dup_paths)
                )

    return true_duplicates


def format_duplicates_as_table(
    duplicate_groups: list[list[str]],
    images_dict: dict[str, list[int]],
    cdn_base_url: str,
    cdn_base_path: str,
    count: int | None = None,
) -> Table:
    """Formate les doublons sous forme de tableau Rich.

    Args:
        duplicate_groups: liste de groupes de chemins d'images dupliquées.
        images_dict: dictionnaire des dimensions pour enrichir l'affichage.
        cdn_base_url: URL de base du CDN.
        cdn_base_path: chemin de base des images.
        count: nombre max de groupes à afficher. Defaults to None (tous).

    Returns:
        Tableau Rich prêt à afficher.
    """
    groups_to_display = duplicate_groups[:count] if count else duplicate_groups

    table = Table(
        title=(
            f"Images en doublon dans le CDN Geotribu - "
            f"{len(duplicate_groups)} groupe(s) trouvé(s)\n"
            "(ctrl+clic sur le chemin pour ouvrir l'image)"
        ),
        show_lines=True,
        caption=f"{__title__} {__version__}",
    )

    table.add_column(header="Groupe", justify="center", style="bright_black")
    table.add_column(header="Chemin relatif", justify="left")
    table.add_column(header="Dimensions", justify="center", style="magenta")
    table.add_column(header="URL complète", justify="left", style="blue")

    for group_index, paths in enumerate(groups_to_display, start=1):
        for i, relative_path in enumerate(paths):
            dims = images_dict.get(relative_path, [0, 0])
            full_url = f"{cdn_base_url}{cdn_base_path}/{relative_path}"

            table.add_row(
                # On n'affiche le numéro de groupe que sur la première ligne
                str(group_index) if i == 0 else "",
                f"[link={full_url}]{relative_path}[/link]",
                f"{dims[0]}×{dims[1]}",
                full_url,
            )

    return table


# ############################################################################
# ########## CLI #################
# ################################


def parser_images_duplicates(
    subparser: argparse.ArgumentParser,
) -> argparse.ArgumentParser:
    """Configure le parser pour la sous-commande de détection des doublons.

    Args:
        subparser: parser à configurer.

    Returns:
        Parser configuré et prêt à l'emploi.
    """
    subparser.add_argument(
        "--check-content",
        action="store_true",
        default=False,
        dest="check_content",
        help="Vérifie le contenu des images candidates par empreinte SHA-256 pour "
        "confirmer les vrais doublons. "
        "ATTENTION : nécessite de télécharger toutes les images candidates depuis le CDN, "
        "ce qui peut prendre du temps selon leur nombre.",
    )

    subparser.add_argument(
        "-n",
        "--results-number",
        default=getenv("GEOTRIBU_RESULTATS_NOMBRE", 20),
        dest="results_number",
        help="Nombre maximum de groupes de doublons à afficher.",
        type=int,
    )

    subparser.add_argument(
        "-o",
        "--format-output",
        choices=["json", "table"],
        default=getenv("GEOTRIBU_RESULTATS_FORMAT", "table"),
        dest="format_output",
        help="Format de sortie.",
        metavar="GEOTRIBU_RESULTATS_FORMAT",
    )

    subparser.add_argument(
        "-r",
        "--remote-index-file",
        default=defaults_settings.cdn_search_index_full_url,
        dest="remote_index_file",
        help="URL de l'index de recherche CDN distant.",
        type=str,
    )

    subparser.add_argument(
        "-l",
        "--local-index-file",
        default=Path().home() / ".geotribu/search/cdn_search_index.json",
        dest="local_index_file",
        help="Chemin vers le fichier d'index local.",
        type=Path,
    )

    subparser.add_argument(
        "-x",
        "--expiration-rotating-hours",
        default=getenv("GEOTRIBU_IMAGES_INDEX_EXPIRATION_HOURS", 24),
        dest="expiration_rotating_hours",
        help="Nombre d'heures avant de considérer l'index local comme périmé.",
        metavar="GEOTRIBU_IMAGES_INDEX_EXPIRATION_HOURS",
        type=int,
    )

    subparser.set_defaults(func=run)

    return subparser


# ############################################################################
# ########## MAIN ################
# ################################


def run(args: argparse.Namespace) -> None:
    """Logique principale de la sous-commande.

    Args:
        args: arguments passés à la sous-commande.
    """
    logger.debug(f"Running {args.command} with {args}")

    # --- Récupération de l'index CDN ---
    args.local_index_file.parent.mkdir(parents=True, exist_ok=True)

    with console.status(
        "Téléchargement/chargement de l'index des images CDN...", spinner="earth"
    ):
        local_index = download_remote_file_to_local(
            remote_url_to_download=args.remote_index_file,
            local_file_path=args.local_index_file,
            expiration_rotating_hours=args.expiration_rotating_hours,
        )

    if not isinstance(local_index, Path):
        logger.error(
            f"Impossible de récupérer l'index depuis {args.remote_index_file}."
        )
        return

    with local_index.open("rb") as fd:
        serialized_idx = orjson.loads(fd.read())

    # L'index CDN contient {"index": <lunr>, "images": {"path": [w, h], ...}}
    images_dict: dict[str, list[int]] = serialized_idx.get("images", {})

    console.print(
        f":frame_with_picture: {len(images_dict)} images indexées dans le CDN."
    )

    # --- Détection des doublons ---
    with console.status(
        "Analyse des dimensions pour identifier les candidats doublons...",
        spinner="dots",
    ):
        duplicate_groups = find_duplicate_images(
            images_dict=images_dict,
            cdn_base_url=defaults_settings.cdn_base_url,
            cdn_base_path=defaults_settings.cdn_base_path,
            check_content=args.check_content,
        )

    if not duplicate_groups:
        verb = (
            "vrais doublons (contenu identique)"
            if args.check_content
            else "candidats doublons (mêmes dimensions)"
        )
        console.print(f":white_check_mark: Aucun {verb} détecté dans le CDN.")
        return

    # --- Affichage des résultats ---
    label = (
        "vrais doublons"
        if args.check_content
        else "candidats doublons (mêmes dimensions)"
    )
    console.print(
        f":warning: {len(duplicate_groups)} groupe(s) de {label} trouvé(s) "
        f"({sum(len(g) for g in duplicate_groups)} images concernées)."
    )

    if not args.check_content:
        console.print(
            "[yellow]Conseil :[/yellow] utilisez [bold]--check-content[/bold] pour "
            "confirmer les vrais doublons par comparaison de contenu (SHA-256)."
        )

    if args.format_output == "table":
        console.print(
            format_duplicates_as_table(
                duplicate_groups=duplicate_groups,
                images_dict=images_dict,
                cdn_base_url=defaults_settings.cdn_base_url,
                cdn_base_path=defaults_settings.cdn_base_path,
                count=args.results_number,
            )
        )
    else:
        # Sortie JSON : liste de groupes avec chemins et URLs complètes
        output = [
            {
                "paths": paths,
                "urls": [
                    f"{defaults_settings.cdn_base_url}{defaults_settings.cdn_base_path}/{p}"
                    for p in paths
                ],
                "dimensions": images_dict.get(paths[0], [0, 0]),
            }
            for paths in duplicate_groups[: args.results_number]
        ]
        console.print_json(orjson.dumps(output).decode())
