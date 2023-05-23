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
from lunr import lunr
from lunr.index import Index
from rich import print
from rich.table import Table

# package
from geotribu_cli.__about__ import __title__, __version__
from geotribu_cli.console import console
from geotribu_cli.constants import GeotribuDefaults
from geotribu_cli.history import CliHistory
from geotribu_cli.utils.date_from_content import get_date_from_content_location
from geotribu_cli.utils.file_downloader import download_remote_file_to_local
from geotribu_cli.utils.file_stats import is_file_older_than
from geotribu_cli.utils.formatters import convert_octets, url_add_utm

# ############################################################################
# ########## GLOBALS #############
# ################################

logger = logging.getLogger(__name__)
defaults_settings = GeotribuDefaults()

# ############################################################################
# ########## FUNCTIONS ###########
# ################################


def filter_content_listing(json_filepath: Path) -> filter:
    """Filtering out irrelevant docs from content listing to reduce number of \
        documents to index.

    Args:
        json_filepath (Path): path to the input JSON file

    Returns:
        filter: filtered object
    """
    with json_filepath.open(mode="rb") as j:
        data: dict = orjson.loads(j.read())

    return filter(
        lambda c: c.get("location").startswith(("article", "rdp")),
        # and not c.get("location").endswith(("#intro", "#introduction")),
        data.get("docs"),
    )


def format_output_result(
    result: list[dict], search_term: str = None, format_type: str = None, count: int = 5
) -> str:
    """Format result according to output option.

    Args:
        result (list[dict]): result to format
        search_term (str, optional): term used for search. Defaults to None.
        format_type (str, optional): format output option. Defaults to None.
        count (int, optional): default number of results to display. Defaults to 5.

    Returns:
        str: formatted result ready to print
    """

    if format_type == "table":
        table = Table(
            title=f"Recherche de contenus - {count}/{len(result)} résultats "
            f"avec le terme : {search_term}\n(ctrl+clic sur le titre pour ouvrir le contenu)",
            show_lines=True,
            highlight=True,
            caption=f"{__title__} {__version__}",
        )

        # columns
        table.add_column(header="#", justify="center")
        table.add_column(header="Titre", justify="left", style="default")
        table.add_column(header="Type", justify="center", style="bright_black")
        table.add_column(
            header="Date de publication", justify="center", style="bright_black"
        )
        table.add_column(header="Score", style="magenta")
        table.add_column(header="Mots-clés", justify="right", style="blue")

        # iterate over results
        for r in result[:count]:
            table.add_row(
                f"{result.index(r)}",
                f"[link={url_add_utm(r.get('url'))}]{r.get('titre')}[/link]",
                r.get("type"),
                f"{r.get('date'):%d %B %Y}",
                r.get("score"),
                ",".join(r.get("tags")),
            )

        return table
    else:
        return result[:count]


def generate_index_from_docs(
    input_documents_to_index: dict,
    index_ref_id: str,
    index_configuration: dict,
    index_fieds_definition: list[dict],
) -> Index:
    """Build search index from input documents.

    Args:
        input_documents_to_index (dict): documents to index
        index_ref_id (str): field to use as index primary key
        index_configuration (dict): index configuration (language, etc.)
        index_fieds_definition (List[dict]): fields settings (boost, etc.)

    Returns:
        Index: lunr Index
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
        help="Terme de recherche. Accepte les filtres sur les champs indexés : tags ou "
        "title. Exemple : 'ubuntu title:qgis'",
        metavar="search-term",
        type=str,
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
        default=getenv("GEOTRIBU_CONTENUS_DEFAULT_TYPE", None),
        help="Filtrer sur un type de contenu en particulier.",
        metavar="GEOTRIBU_CONTENUS_DEFAULT_TYPE",
    )

    subparser.add_argument(
        "-n",
        "--results-number",
        default=getenv("GEOTRIBU_RESULTATS_NOMBRE", 5),
        dest="results_number",
        help="Nombre de résultats à retourner.",
        metavar="GEOTRIBU_RESULTATS_NOMBRE",
        type=int,
    )

    subparser.add_argument(
        "-x",
        "--expiration-rotating-hours",
        default=getenv("GEOTRIBU_CONTENUS_INDEX_EXPIRATION_HOURS", 24 * 7),
        dest="expiration_rotating_hours",
        help="Nombre d'heures à partir duquel considérer le fichier local comme périmé.",
        metavar="GEOTRIBU_CONTENUS_INDEX_EXPIRATION_HOURS",
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
        dest="format_output",
        help="Format de sortie.",
        metavar="GEOTRIBU_RESULTATS_FORMAT",
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
    logger.debug(f"Running {args.command} with {args}")

    # local vars
    history = CliHistory()

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
        with console.status(
            "Téléchargement de la liste des contenus...", spinner="earth"
        ):
            get_local_contents_listing = download_remote_file_to_local(
                remote_url_to_download=args.remote_index_file,
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

        # filtre les contenus qui ne sont ni des articles, ni des revues de presse
        contents_listing = tuple(filter_content_listing(local_listing_file))
        with local_listing_file.open(mode="wb") as fd:
            fd.write(orjson.dumps(contents_listing))

        with console.status("Génère l'index de recherche local...", spinner="earth"):
            # build index from contents listing
            idx = generate_index_from_docs(
                input_documents_to_index=tuple(contents_listing),
                index_ref_id="location",
                index_configuration={"lang": "fr"},
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

        with args.local_index_file.open(mode="wb") as fd:
            # json.dump(serialized_idx, fd, separators=(",", ":"))
            fd.write(orjson.dumps(serialized_idx))

        logger.info(
            f"Local index generated into {args.local_index_file} "
            f"from contents listing ({local_listing_file})."
        )
    else:
        # load
        with local_listing_file.open("rb") as fd:
            contents_listing = orjson.loads(fd.read())

        # load previously built index
        logger.info(
            f"Local index file ({args.local_index_file}) exists and is not "
            f"older than {args.expiration_rotating_hours} hour(s). "
            "Lets use it to perform search."
        )
        with args.local_index_file.open("rb") as fd:
            serialized_idx = orjson.loads(fd.read())
        idx = Index.load(serialized_idx)

    # recherche
    with console.status(f"Recherche {args.search_term}...", spinner="earth"):
        search_results: list[dict] = idx.search(args.search_term)

    if not len(search_results):
        print(
            f":person_shrugging: Aucun contenu trouvé pour : {args.search_term}"
            "\nRéessayer en utilisant des paramètres de recherche moins stricts. "
            f"Exemple : '*{args.search_term}*'"
        )
        sys.exit(0)

    # résultats : enrichissement et filtre
    with console.status(
        f"Enrichissement des {len(search_results)} résultats...", spinner="earth"
    ):
        final_results: list[dict] = []

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

            # crée un résultat de sortie
            out_result = {
                "titre": result.get("title"),
                "type": "Article"
                if result.get("ref").startswith("articles/")
                else "GeoRDP",
                "date": get_date_from_content_location(result.get("ref")),
                "score": f"{result.get('score'):.3}",
                "url": f"{defaults_settings.site_base_url}{result.get('ref')}",
            }

            final_results.append(out_result)

        final_urls = [rez.get("url") for rez in final_results]
        matched_docs = {
            f"{defaults_settings.site_base_url}{c.get('location')}": (
                c.get("title"),
                c.get("tags"),
            )
            for c in contents_listing
            if f"{defaults_settings.site_base_url}{c.get('location')}" in final_urls
        }

        for rezult in final_results:
            rezult["titre"], rezult["tags"] = matched_docs.get(rezult.get("url"))

    # formatage de la sortie
    if len(final_results):
        print(
            format_output_result(
                result=final_results,
                search_term=args.search_term,
                format_type=args.format_output,
                count=args.results_number,
            )
        )
    else:
        print(f":person_shrugging: Aucun contenu trouvé pour : {args.search_term}")
        sys.exit(0)

    # save into history
    history.dump(
        cmd_name=__name__.split(".")[-1],
        results_to_dump=final_results,
        request_performed=args.search_term,
    )


# -- Stand alone execution
if __name__ == "__main__":
    pass
