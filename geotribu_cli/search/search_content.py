#! python3  # noqa: E265

# ############################################################################
# ########## IMPORTS #############
# ################################

# standard library
import argparse
import logging
import sys
from datetime import date
from os import getenv
from pathlib import Path

# 3rd party
import orjson
from lunr import lunr
from lunr.index import Index
from rich.prompt import Prompt

# package
from geotribu_cli.cli_results_rich_formatters import format_output_result_search_content
from geotribu_cli.console import console
from geotribu_cli.constants import GeotribuDefaults
from geotribu_cli.history import CliHistory
from geotribu_cli.subcommands.open_result import open_content
from geotribu_cli.utils.args_types import arg_date_iso_max_today
from geotribu_cli.utils.dates_manipulation import (
    get_date_from_content_location,
    is_more_recent,
)
from geotribu_cli.utils.file_downloader import download_remote_file_to_local
from geotribu_cli.utils.file_stats import is_file_older_than
from geotribu_cli.utils.formatters import convert_octets
from geotribu_cli.utils.str2bool import str2bool

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
        default=defaults_settings.geotribu_working_folder.joinpath(
            "search/site_search_index.json"
        ),
        type=Path,
        dest="local_index_file",
    )

    subparser.add_argument(
        "-f",
        "-ft",
        "--filter-type",
        choices=["article", "rdp"],
        default=getenv("GEOTRIBU_CONTENUS_DEFAULT_TYPE", None),
        help="Filtrer sur un type de contenu en particulier.",
        metavar="GEOTRIBU_CONTENUS_DEFAULT_TYPE",
    )

    subparser.add_argument(
        "-ds",
        "--depuis",
        "--date-start",
        default=getenv("GEOTRIBU_CONTENUS_START_DATE", "2020-01-01"),
        dest="filter_date_start",
        help="Date la plus ancienne sur laquelle filtrer les contenus "
        "(format: AAAA-MM-JJ). Valeur par défaut : 2020-01-01",
        metavar="GEOTRIBU_CONTENUS_DATE_START",
        type=arg_date_iso_max_today,
    )

    subparser.add_argument(
        "-de",
        "--jusqua",
        "--date-end",
        default=getenv("GEOTRIBU_CONTENUS_END_DATE", f"{date.today():%Y-%m-%d}"),
        dest="filter_date_end",
        help="Date la plus récente sur laquelle filtrer les contenus "
        "(format: AAAA-MM-JJ). Valeur par défault : date du jour.",
        metavar="GEOTRIBU_CONTENUS_DATE_END",
        type=arg_date_iso_max_today,
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

    subparser.add_argument(
        "-a",
        "--no-fusion-par-url",
        default=str2bool(getenv("GEOTRIBU_MERGE_CONTENT_BY_UNIQUE_URL", True)),
        action="store_false",
        dest="opt_merge_unique_url",
        help="Désactive la fusion des contenus par URL. Les résultats contiendront "
        "donc potentiellement donc différentes sections d'un même article.",
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
        console.print(
            f":person_shrugging: Aucun contenu trouvé pour : {args.search_term}"
            "\nRéessayer en utilisant des paramètres de recherche moins stricts. "
            f"Exemple : '*{args.search_term}*'"
        )
        sys.exit(0)

    # résultats : enrichissement et filtre
    count_ignored_results = 0
    unique_ref: list = []
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
                count_ignored_results += 1
                continue
            elif args.filter_type == "rdp" and not result.get("ref").startswith("rdp/"):
                logger.debug(
                    f"Résultat ignoré par le filtre {args.filter_type}: {result.get('ref')}"
                )
                count_ignored_results += 1
                continue
            else:
                pass

            # filtrer les contenus qui ne correspondent pas aux années sélectionnées
            rezult_date = get_date_from_content_location(result.get("ref"))
            if isinstance(args.filter_date_start, date) and not is_more_recent(
                date_ref=args.filter_date_start, date_to_compare=rezult_date
            ):
                logger.info(
                    f"Résultat {result.get('ref')} ignoré car plus ancien "
                    f"({rezult_date}) que la date minimum {args.filter_date_start}"
                )
                count_ignored_results += 1
                continue
            elif isinstance(args.filter_date_end, date) and is_more_recent(
                date_ref=args.filter_date_end, date_to_compare=rezult_date
            ):
                logger.info(
                    f"Résultat {result.get('ref')} ignoré car plus récent "
                    f"({rezult_date}) que la date maximum {args.filter_date_end}."
                )
                count_ignored_results += 1
                continue

            if (
                args.opt_merge_unique_url
                and result.get("ref").startswith("articles/")
                and "#" in result.get("ref")
                and result.get("ref").split("#")[0] in unique_ref
            ):
                logger.info(
                    f"Résultat {result.get('ref')} ignoré car il s'agit d'une "
                    f"sous-partie ({result.get('ref').split('#')[1]}) d'un article déjà "
                    "présent dans les résultats."
                )
                count_ignored_results += 1
                continue

            unique_ref.append(result.get("ref").split("#")[0])

            # crée un résultat de sortie
            out_result = {
                "type": (
                    "Article" if result.get("ref").startswith("articles/") else "GeoRDP"
                ),
                "date": rezult_date,
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
        console.print(
            format_output_result_search_content(
                result=final_results,
                search_term=args.search_term,
                format_type=args.format_output,
                count=args.results_number,
                search_filter_dates=(args.filter_date_start, args.filter_date_end),
                search_filter_type=args.filter_type,
            )
        )
    else:
        console.print(
            f":person_shrugging: Aucun contenu trouvé pour : {args.search_term} parmi "
            f"les {len(search_results)} résultats de recherche. "
            f"{count_ignored_results} résultats ignorés par les filtres (type, dates)..."
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
