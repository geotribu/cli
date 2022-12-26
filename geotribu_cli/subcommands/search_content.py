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
from typing import List

# 3rd party
from lunr import lunr
from lunr.index import Index

# package
from geotribu_cli.constants import GeotribuDefaults
from geotribu_cli.utils.file_downloader import download_remote_file_to_local
from geotribu_cli.utils.file_stats import is_file_older_than
from geotribu_cli.utils.formatters import convert_octets

# ############################################################################
# ########## GLOBALS #############
# ################################

logger = logging.getLogger(__name__)
defaults_settings = GeotribuDefaults()

# ############################################################################
# ########## FUNCTIONS ###########
# ################################


def generate_index_from_docs(
    input_documents_to_index: dict,
    index_ref_id: str,
    index_configuration: dict,
    index_fieds_definition: List[dict],
) -> Index:
    """_summary_

    Args:
        input_documents_to_index (dict): _description_
        index_ref_id (str): _description_
        index_configuration (dict): _description_
        index_fieds_definition (List[dict]): _description_

    Returns:
        Index: _description_
    """

    idx: Index = lunr(
        ref=index_ref_id,
        fields=index_fieds_definition,
        documents=input_documents_to_index,
        languages=index_configuration.get("lang", "fr"),
    )

    return idx


# ############################################################################
# ########## CLI #################
# ################################


def parser_search_content(
    subparser: argparse.ArgumentParser,
) -> argparse.ArgumentParser:
    """Set the argument parser for search-content subcommand.

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
        default=defaults_settings.site_search_index_full_url,
        type=str,
        dest="remote_index_file",
    )

    subparser.add_argument(
        "--local-index-file",
        help="Emplacement du fichier local.",
        default=Path().home() / ".geotribu/search/site_search_index.json",
        type=Path,
        dest="local_index_file",
    )

    subparser.add_argument(
        "--filter-type",
        choices=["article", "rdp"],
        default=None,
        help="Filtrer sur un type de contenu en particulier.",
    )

    subparser.add_argument(
        "--expiration-rotating-hours",
        help="Nombre d'heures à partir de quand considérer le fichier local comme périmé.",
        default=24 * 7,
        type=int,
        dest="expiration_rotating_hours",
    )

    subparser.set_defaults(func=run)

    return subparser


# ############################################################################
# ########## MAIN ################
# ################################


def run(args: argparse.Namespace):
    """Run the sub command logic.

    There are 2 files involved (names can vary):

    - `site_content_listing.json`: the downloaded file from the website which is \
        just a listing of contents
    - `site_search_index.json` (= args.local_index_file): the file with the indexed \
        contents with lunr built locally from the listing file.

    Process:

    #. Check if the local index file exists and is up to date
    #. If not:
        #. Download the website contents listing from remote
        #. Generate a local index from the contents listing
    #. Load the local index
    #. Perform the search

    Args:
        args (argparse.Namespace): arguments passed to the subcommand
    """
    print(f"Running {args.command} with {args}")

    args.local_index_file.parent.mkdir(parents=True, exist_ok=True)

    #  local contents listing file
    local_listing_file = Path(
        args.local_index_file.parent / "site_content_listing.json"
    )

    # check local file index
    if not args.local_index_file.exists() or is_file_older_than(
        args.local_index_file, args.expiration_rotating_hours
    ):
        # if the local index doesn't exist or exists but it's outdated: download the
        # listing from website
        get_local_contents_listing = download_remote_file_to_local(
            url_index_to_download=args.remote_index_file,
            local_file_path=local_listing_file,
            expiration_rotating_hours=args.expiration_rotating_hours,
        )
        if not isinstance(get_local_contents_listing, Path):
            logger.error(
                f"Le téléchargement du fichier distant {args.remote_index_file} "
                f"ou la récupération du fichier local {local_listing_file} a échoué."
            )
            if isinstance(get_local_contents_listing, Exception):
                logger.error(get_local_contents_listing)
            sys.exit()
        logger.info(
            f"Local listing file: {local_listing_file}, "
            f"{convert_octets(local_listing_file.stat().st_size)}"
        )

        # build index from contents listing
        with local_listing_file.open("r", encoding=("UTF-8")) as fd:
            contents_listing = json.loads(fd.read())
        idx = generate_index_from_docs(
            input_documents_to_index=contents_listing.get("docs"),
            index_ref_id="location",
            index_configuration=contents_listing.get("config", {"lang": "fr"}),
            index_fieds_definition=[
                dict(field_name="title", boost=10),
                dict(field_name="tags", boost=5, extractor=lambda d: d or None),
                "text",
                "location",
            ],
        )

        # save it as JSON file for next time
        serialized_idx = idx.serialize()

        # export into a JSON file
        args.local_index_file.unlink(missing_ok=True)

        with args.local_index_file.open(mode="w", encoding="UTF-8") as fd:
            json.dump(serialized_idx, fd, sort_keys=True, separators=(",", ":"))

        logger.info(
            f"Local index generated into {args.local_index_file} "
            f"from contents listing ({local_listing_file})."
        )
    else:
        logger.info(
            f"Local index file ({args.local_index_file}) exists and is not "
            f"older than {args.expiration_rotating_hours} hour(s). "
            "Lets use it to perform search."
        )
        with args.local_index_file.open("r") as fd:
            serialized_idx = json.loads(fd.read())
        idx = Index.load(serialized_idx)

    # recherche
    search_results: list[dict] = idx.search(f"*{args.search_term}*")

    for search_result in search_results:
        search_result.update(
            {
                "full_url": f"{defaults_settings.site_base_url}/{search_result.get('ref')}",
            }
        )

    print(search_results)


# -- Stand alone execution
if __name__ == "__main__":
    pass
