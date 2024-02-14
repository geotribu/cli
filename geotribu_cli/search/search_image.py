#! python3  # noqa: E265

# ############################################################################
# ########## IMPORTS #############
# ################################

# standard library
import argparse
import logging
import sys
from os import getenv
from pathlib import Path

# 3rd party
import orjson
from lunr.index import Index
from rich.prompt import Prompt

# package
from geotribu_cli.cli_results_rich_formatters import format_output_result_search_image
from geotribu_cli.console import console
from geotribu_cli.constants import GeotribuDefaults
from geotribu_cli.history import CliHistory
from geotribu_cli.subcommands.open_result import open_content
from geotribu_cli.utils.file_downloader import download_remote_file_to_local
from geotribu_cli.utils.formatters import convert_octets
from geotribu_cli.utils.str2bool import str2bool

# ############################################################################
# ########## GLOBALS #############
# ################################

logger = logging.getLogger(__name__)
defaults_settings = GeotribuDefaults()

# ############################################################################
# ########## CLI #################
# ################################


def parser_search_image(subparser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """Set the argument parser for search-image subcommand.

    Args:
        subparser (argparse.ArgumentParser): parser to set up

    Returns:
        argparse.ArgumentParser: parser ready to use
    """
    subparser.add_argument(
        "search_term",
        help="Terme de recherche.",
        type=str,
        metavar="search-term",
    )

    subparser.add_argument(
        "-r",
        "--remote-index-file",
        help="Emplacement du fichier distant.",
        default=defaults_settings.cdn_search_index_full_url,
        type=str,
        dest="remote_index_file",
    )

    subparser.add_argument(
        "-l",
        "--local-index-file",
        help="Emplacement du fichier local.",
        default=Path().home() / ".geotribu/search/cdn_search_index.json",
        type=Path,
        dest="local_index_file",
    )

    subparser.add_argument(
        "-f",
        "--filter-type",
        choices=["logo", "geoicone"],
        default=getenv("GEOTRIBU_IMAGES_DEFAULT_TYPE", None),
        help="Filtrer sur un type d'images en particulier.",
        dest="filter_type",
        metavar="GEOTRIBU_IMAGES_DEFAULT_TYPE",
    )

    subparser.add_argument(
        "-n",
        "--results-number",
        default=getenv("GEOTRIBU_RESULTATS_NOMBRE", 5),
        help="Nombre de résultats à retourner.",
        dest="results_number",
        metavar="GEOTRIBU_RESULTATS_NOMBRE",
        type=int,
    )

    subparser.add_argument(
        "-x",
        "--expiration-rotating-hours",
        help="Nombre d'heures à partir duquel considérer le fichier local comme périmé.",
        default=getenv("GEOTRIBU_IMAGES_INDEX_EXPIRATION_HOURS", 24),
        dest="expiration_rotating_hours",
        metavar="GEOTRIBU_IMAGES_INDEX_EXPIRATION_HOURS",
        type=int,
    )

    subparser.add_argument(
        "-o",
        "--format-output",
        choices=[
            "json",
            "table",
        ],
        default=getenv("GEOTRIBU_RESULTATS_FORMAT", "table"),
        help="Format de sortie.",
        dest="format_output",
        metavar="GEOTRIBU_RESULTATS_FORMAT",
    )

    subparser.add_argument(
        "--no-prompt",
        default=str2bool(getenv("GEOTRIBU_PROMPT_AFTER_SEARCH", True)),
        action="store_false",
        dest="opt_prompt_disabled",
        help="Désactive le prompt demandant le résultat à ouvrir à la fin de la commande.",
    )

    subparser.set_defaults(func=run)

    return subparser


# ############################################################################
# ########## MAIN ################
# ################################


def run(args: argparse.Namespace):
    """Run the sub command logic.

    Perform a search on images stored on the Geotribu pseudo-CDN \
        (<https://cdn.geotribu.fr/>).

    Args:
        args (argparse.Namespace): arguments passed to the subcommand
    """
    logger.debug(f"Running {args.command} with {args}")

    # local vars
    history = CliHistory()

    args.local_index_file.parent.mkdir(parents=True, exist_ok=True)

    with console.status("Téléchargement de la liste des images...", spinner="earth"):
        # get local search index
        get_or_update_local_search_index = download_remote_file_to_local(
            remote_url_to_download=args.remote_index_file,
            local_file_path=args.local_index_file,
            expiration_rotating_hours=args.expiration_rotating_hours,
        )
    if not isinstance(get_or_update_local_search_index, Path):
        logger.error(
            f"Le téléchargement du fichier distant {args.remote_index_file} "
            f"ou la récupération du fichier local {args.local_index_file} a échoué."
        )
        if isinstance(get_or_update_local_search_index, Exception):
            logger.error(get_or_update_local_search_index)
        sys.exit()
    logger.info(
        f"Local index file: {args.local_index_file}, "
        f"{convert_octets(args.local_index_file.stat().st_size)}"
    )

    # load the local index file
    if not args.local_index_file.exists():
        logger.error(f"{args.local_index_file.resolve()} does not exist")
        sys.exit(f"{args.local_index_file.resolve()} does not exist")
    # loads it
    with args.local_index_file.open("rb") as fd:
        serialized_idx = orjson.loads(fd.read())

    # charge l'index sérialisé
    idx = Index.load(serialized_idx.get("index"))
    images_dict = serialized_idx.get("images")

    # recherche
    with console.status(f"Recherche {args.search_term}...", spinner="earth"):
        search_results: list[dict] = idx.search(args.search_term)

    if not len(search_results):
        console.print(
            f":person_shrugging: Aucune image trouvée pour : {args.search_term}"
        )
        sys.exit(0)

    # résultats : enrichissement et filtre
    final_results = []

    for result in search_results:
        # filter on image type
        if args.filter_type == "logo" and not result.get("ref").startswith(
            "logos-icones/"
        ):
            logger.debug(
                f"Résultat ignoré par le filtre {args.filter_type}: {result.get('ref')}"
            )
            continue
        elif args.filter_type == "geoicone" and not result.get("ref").startswith(
            "internal/icons-rdp-news/"
        ):
            logger.debug(
                f"Résultat ignoré par le filtre {args.filter_type}: {result.get('ref')}"
            )
            continue
        else:
            pass

        mapped_img = images_dict.get(result.get("ref"))

        # crée un résultat de sortie
        out_result = {
            "nom": result.get("ref").split("/")[-1],
            "dimensions": f"{mapped_img[0]}x{mapped_img[1]}",
            "score": f"{result.get('score'):.3}",
            "cdn_path": f"{result.get('ref')}",
            "url": f"{defaults_settings.cdn_base_url}"
            f"{defaults_settings.cdn_base_path}/"
            f"{result.get('ref')}",
        }

        final_results.append(out_result)

    # formatage de la sortie
    if len(final_results):
        console.print(
            format_output_result_search_image(
                result=final_results,
                format_type=args.format_output,
                count=args.results_number,
                search_term=args.search_term,
                search_filter_type=args.filter_type,
            )
        )
    else:
        console.print(
            f":person_shrugging: Aucune image trouvée pour : {args.search_term}"
        )
        sys.exit(0)

    # save into history
    history.dump(
        cmd_name=__name__.split(".")[-1],
        results_to_dump=final_results,
        request_performed=args.search_term,
    )

    # prompt to open a result
    if args.opt_prompt_disabled:
        result_to_open = Prompt.ask(
            prompt="Afficher le résultat n° (q pour quitter)",
            console=console,
            choices=["q"]
            + [
                str(i) for i in range(0, min([len(final_results), args.results_number]))
            ],
            default="q",
        )

        if result_to_open == "q":
            sys.exit(0)

        open_content(
            content_uri=final_results[int(result_to_open)].get("url"),
            application=getenv("GEOTRIBU_OPEN_WITH", "shell"),
        )
