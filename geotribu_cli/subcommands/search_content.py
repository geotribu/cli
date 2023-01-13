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
from rich import print
from rich.table import Table

# package
from geotribu_cli.__about__ import __title__, __version__
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
            title=f"Recherche de contenus - {len(result)} résultats "
            f"avec le terme : {search_term}",
            show_lines=True,
            highlight=True,
            caption=f"{__title__} {__version__}",
        )

        # determine row from first item
        for k in result[0].keys():
            table.add_column(header=k.title(), justify="right")

        # iterate over results
        for r in result[:count]:

            table.add_row(
                r.get("titre"),
                r.get("type"),
                r.get("score"),
                r.get("url"),
            )

        return table
    else:
        return result


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
        "-r",
        "--remote-index-file",
        help="Emplacement du fichier distant.",
        default=defaults_settings.site_search_index_full_url,
        type=str,
        dest="remote_index_file",
    )

    subparser.add_argument(
        "-l",
        "--local-index-file",
        help="Emplacement du fichier local.",
        default=Path().home() / ".geotribu/search/site_search_index.json",
        type=Path,
        dest="local_index_file",
    )

    subparser.add_argument(
        "-f",
        "--filter-type",
        choices=["article", "rdp"],
        default=None,
        help="Filtrer sur un type de contenu en particulier.",
    )

    subparser.add_argument(
        "-x",
        "--expiration-rotating-hours",
        help="Nombre d'heures à partir duquel considérer le fichier local comme périmé.",
        default=24 * 7,
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
            index_ref_id="location".split("#")[0],
            index_configuration=contents_listing.get("config", {"lang": "fr"}),
            index_fieds_definition=[
                dict(field_name="title", boost=10),
                dict(field_name="tags", boost=5),
                dict(field_name="text"),
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
    search_results: list[dict] = idx.search(f"{args.search_term}*")

    # résultats : enrichissement et filtre
    final_results = []

    for result in search_results:
        # filter on content type
        if args.filter_type == "article" and not result.get("ref").startswith(
            "articles/"
        ):
            logger.debug(
                f"Résultat ignoré par le filtre {args.filter_type}: {result.get('ref')}"
            )
            continue
        elif args.filter_type == "rdp" and not result.get("ref").startswith("rdp/"):
            logger.debug(
                f"Résultat ignoré par le filtre {args.filter_type}: {result.get('ref')}"
            )
            continue
        else:
            pass

        result.update({})

        # crée un résultat de sortie
        out_result = {
            "titre": result.get("title"),
            "type": "Article"
            if result.get("ref").startswith("articles/")
            else "GeoRDP",
            "score": f"{result.get('score'):.3}",
            "url": f"{defaults_settings.site_base_url}{result.get('ref')}",
        }

        final_results.append(out_result)

    # formatage de la sortie
    print(
        format_output_result(
            result=final_results,
            search_term=args.search_term,
            format_type=args.format_output,
            count=args.results_number,
        )
    )


# -- Stand alone execution
if __name__ == "__main__":
    pass
