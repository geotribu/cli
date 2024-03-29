#! python3  # noqa: E265

# ############################################################################
# ########## IMPORTS #############
# ################################

# standard library
import argparse
import logging
import sys
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from os import getenv
from pathlib import Path

# 3rd party
from rich.prompt import Prompt
from rich.table import Table

# package
from geotribu_cli.__about__ import __title__, __version__
from geotribu_cli.console import console
from geotribu_cli.constants import GeotribuDefaults
from geotribu_cli.history import CliHistory
from geotribu_cli.rss.mdl_rss import RssItem
from geotribu_cli.subcommands.open_result import open_content
from geotribu_cli.utils.file_downloader import download_remote_file_to_local
from geotribu_cli.utils.formatters import convert_octets, url_add_utm
from geotribu_cli.utils.str2bool import str2bool

# ############################################################################
# ########## GLOBALS #############
# ################################

logger = logging.getLogger(__name__)
defaults_settings = GeotribuDefaults()

# ############################################################################
# ########## FUNCTIONS ###########
# ################################


def format_output_result(
    result: list[RssItem], format_type: str = None, count: int = 5
) -> str:
    """Format result according to output option.

    Args:
        result (list[RssItem]): result to format
        format_type (str, optional): format output option. Defaults to None.
        count (int, optional): default number of results to display. Defaults to 5.

    Returns:
        str: formatted result ready to print
    """

    if format_type == "table":
        table = Table(
            title=f"{count} derniers contenus publiés",
            show_lines=True,
            # highlight=True,
            caption=f"{__title__} {__version__}",
        )

        table.add_column(header="#", justify="center")
        table.add_column(header="Titre", justify="left", style="default")
        table.add_column(
            header="Date de publication", justify="center", style="bright_black"
        )
        table.add_column(header="Auteur/e", style="magenta")
        table.add_column(header="Mots-clés", style="blue")

        # iterate over results
        for r in result[:count]:
            table.add_row(
                f"{result.index(r)}",
                f"[link={url_add_utm(r.url)}]{r.title}[/link]",
                f"{r.date_pub:%d %B %Y}",
                r.author,
                ",".join(r.categories),
            )

        return table
    else:
        return result[:count]


# ############################################################################
# ########## CLI #################
# ################################


def parser_latest_content(
    subparser: argparse.ArgumentParser,
) -> argparse.ArgumentParser:
    """Set the argument parser for subcommand.

    Args:
        subparser (argparse.ArgumentParser): parser to set up

    Returns:
        argparse.ArgumentParser: parser ready to use
    """
    subparser.add_argument(
        "-r",
        "--remote-index-file",
        help="Emplacement du fichier distant.",
        default=defaults_settings.rss_created_full_url,
        type=str,
        dest="remote_index_file",
    )

    subparser.add_argument(
        "-l",
        "--local-index-file",
        help="Emplacement du fichier local.",
        default=Path().home() / ".geotribu/rss/rss.xml",
        type=Path,
        dest="local_index_file",
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
        default="table",
        help="Format de sortie.",
        dest="format_output",
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

    Download the RSS feed file and display results.

    Args:
        args (argparse.Namespace): arguments passed to the subcommand
    """
    logger.debug(f"Running {args.command} with {args}")

    # local vars
    history = CliHistory()

    args.local_index_file.parent.mkdir(parents=True, exist_ok=True)

    # get local search index
    with console.status("Téléchargement du flux RSS...", spinner="earth"):
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
            f"Fichier RSS local : {args.local_index_file}, "
            f"{convert_octets(args.local_index_file.stat().st_size)}"
        )

    # Parse the feed
    with console.status("Lecture du fichier local...", spinner="earth"):
        feed = ET.parse(args.local_index_file)
        feed_items: list[RssItem] = []

        # Find all articles in the feed
        for item in feed.findall(".//item"):
            try:
                # filter on content type
                if args.filter_type == "article" and not item.find(
                    "link"
                ).text.startswith(f"{defaults_settings.site_base_url}articles/"):
                    logger.debug(
                        f"Résultat ignoré par le filtre {args.filter_type}: {item.find('link').text}"
                    )
                    continue
                elif args.filter_type == "rdp" and not item.find(
                    "link"
                ).text.startswith(f"{defaults_settings.site_base_url}rdp/"):
                    logger.debug(
                        f"Résultat ignoré par le filtre {args.filter_type}: {item.find('link').text}"
                    )
                    continue
                else:
                    pass

                # add items to the feed
                feed_items.append(
                    RssItem(
                        abstract=item.find("description").text,
                        author=item.find("author").text or None,
                        categories=[cat.text for cat in item.findall("category")],
                        date_pub=parsedate_to_datetime(item.find("pubDate").text),
                        image_length=item.find("enclosure").attrib.get("length"),
                        image_type=item.find("enclosure").attrib.get("type"),
                        image_url=item.find("enclosure").attrib.get("url"),
                        guid=item.find("guid").text,
                        title=item.find("title").text,
                        url=item.find("link").text,
                    )
                )
            except Exception as err:
                err_msg = "Feed item (index = {}) triggers an error. Trace: {}".format(
                    feed_items.index(item), err
                )
                logger.error(err_msg)
                sys.exit(err_msg)

    # formatage de la sortie
    console.print(
        format_output_result(
            result=feed_items, format_type=args.format_output, count=args.results_number
        )
    )

    # save into history
    history.dump(
        cmd_name=__name__.split(".")[-1],
        results_to_dump=[{"url": i.url} for i in feed_items],
    )

    # prompt to open a result
    if args.opt_prompt_disabled:
        result_to_open = Prompt.ask(
            prompt="Afficher le résultat n° (q pour quitter)",
            console=console,
            choices=["q"]
            + [str(i) for i in range(0, min([len(feed_items), args.results_number]))],
            default="q",
        )

        if result_to_open == "q":
            sys.exit(0)

        open_content(
            content_uri=feed_items[int(result_to_open)].url,
            application=getenv("GEOTRIBU_OPEN_WITH", "shell"),
        )
