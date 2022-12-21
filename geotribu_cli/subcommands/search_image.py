#! python3  # noqa: E265

# ############################################################################
# ########## IMPORTS #############
# ################################

# standard library
import argparse
import json
import logging
import sys
from pathlib import Path

# 3rd party
from lunr.index import Index

# package
from geotribu_cli.constants import GeotribuDefaults
from geotribu_cli.utils.file_downloader import download_remote_file_to_local
from geotribu_cli.utils.formatters import convert_octets

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
        "--remote-index-file",
        help="Emplacement du fichier distant.",
        default=defaults_settings.cdn_search_index_full_url,
        type=str,
        dest="remote_index_file",
    )

    subparser.add_argument(
        "--local-index-file",
        help="Emplacement du fichier local.",
        default=Path().home() / ".geotribu/search/cdn_search_index.json",
        type=Path,
        dest="local_index_file",
    )

    subparser.add_argument(
        "--filter-type",
        choices=["logo", "geoicone"],
        default=None,
        help="Filtrer sur un type d'images en particulier.",
    )

    subparser.add_argument(
        "--expiration-rotating-hours",
        help="Nombre d'heures à partir de quand considérer le fichier local comme périmé.",
        default=24,
        type=int,
        dest="expiration_rotating_hours",
    )

    subparser.set_defaults(func=run)

    return subparser


# ############################################################################
# ########## MAIN ################
# ################################


def run(args):
    """Run the sub command logic.

    Args:
        args (_type_): _description_
    """
    logger.debug(f"Running {args.command} with {args}")

    args.local_index_file.parent.mkdir(parents=True, exist_ok=True)

    # get local search index
    get_or_update_local_search_index = download_remote_file_to_local(
        url_index_to_download=args.remote_index_file,
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
    with args.local_index_file.open("r") as fd:
        serialized_idx = json.loads(fd.read())

    # charge l'index sérialisé
    idx = Index.load(serialized_idx.get("index"))
    images_dict = serialized_idx.get("images")

    # recherche
    search_results: list[dict] = idx.search(f"*{args.search_term}*")

    for search_result in search_results:
        mapped_img = images_dict.get(search_result.get("ref"))
        search_result.update(
            {
                "width": mapped_img[0],
                "height": mapped_img[1],
                "full_url": f"{defaults_settings.cdn_base_url}"
                f"{defaults_settings.cdn_base_path}/"
                f"{search_result.get('ref')}",
            }
        )

    print(search_results)


# -- Stand alone execution
if __name__ == "__main__":
    pass
