#! python3  # noqa: E265

# ############################################################################
# ########## IMPORTS #############
# ################################

# standard library
import argparse
import logging
import sys
from pathlib import Path

# 3rd party
import orjson
from lunr.index import Index
from rich import print
from rich.table import Table

# package
from geotribu_cli.__about__ import __title__, __version__
from geotribu_cli.constants import GeotribuDefaults
from geotribu_cli.utils.file_downloader import download_remote_file_to_local
from geotribu_cli.utils.formatters import convert_octets

# ############################################################################
# ########## GLOBALS #############
# ################################

logger = logging.getLogger(__name__)
defaults_settings = GeotribuDefaults()

# ############################################################################
# ########## FUNCTIONS ###########
# ################################


def format_output_result(
    result: list[dict], search_term: str = None, format_type: str = None, count: int = 5
) -> str:
    """Format result according to output option.

    Args:
        result (list[dict]): result to format
        search_term (str, optional): term used for search. Defaults to None.
        format_type (str, optional): format output option. Defaults to None.
        count (int, optional): _description_. Defaults to 5.

    Returns:
        str: formatted result ready to print
    """

    if format_type == "table":
        table = Table(
            title=f"Recherche d'images - {len(result)} résultats "
            f"avec le terme : {search_term}",
            show_lines=True,
            highlight=True,
            caption=f"{__title__} {__version__}",
        )

        # columns
        table.add_column(header="Nom", justify="left", style="default")
        table.add_column(header="Dimensions", justify="center", style="bright_black")
        table.add_column(header="Score", style="magenta")
        table.add_column(header="URL", justify="right", style="blue")

        # iterate over results
        for r in result[:count]:

            table.add_row(
                r.get("nom"),
                r.get("dimensions"),
                r.get("score"),
                r.get("url"),
            )

        return table
    else:
        return result


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
        default=None,
        help="Filtrer sur un type d'images en particulier.",
        dest="filter_type",
    )

    subparser.add_argument(
        "-n",
        "--results-number",
        type=int,
        default=5,
        help="Nombre de résultats à retourner.",
        dest="results_number",
    )

    subparser.add_argument(
        "-x",
        "--expiration-rotating-hours",
        help="Nombre d'heures à partir duquel considérer le fichier local comme périmé.",
        default=24,
        type=int,
        dest="expiration_rotating_hours",
    )

    subparser.add_argument(
        "-o",
        "--format-output",
        choices=[
            "table",
        ],
        default=None,
        help="Format de sortie.",
        dest="format_output",
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

    args.local_index_file.parent.mkdir(parents=True, exist_ok=True)

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
    search_results: list[dict] = idx.search(f"*{args.search_term}*")

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
            "url": f"{defaults_settings.cdn_base_url}"
            f"{defaults_settings.cdn_base_path}/"
            f"{result.get('ref')}",
        }

        final_results.append(out_result)

    # formatage de la sortie
    print(
        format_output_result(
            result=final_results,
            format_type=args.format_output,
            count=args.results_number,
        )
    )


# -- Stand alone execution
if __name__ == "__main__":
    pass
