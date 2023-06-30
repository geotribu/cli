#! python3  # noqa: E265

# ############################################################################
# ########## IMPORTS #############
# ################################

# standard library
import argparse
import json
import logging
import sys
from os import getenv
from typing import Literal

# 3rd party
from rich import print
from rich.table import Table

# package
from geotribu_cli.__about__ import __title__, __version__
from geotribu_cli.comments.mdl_comment import Comment
from geotribu_cli.constants import GeotribuDefaults
from geotribu_cli.utils.file_downloader import download_remote_file_to_local

# ############################################################################
# ########## GLOBALS #############
# ################################

logger = logging.getLogger(__name__)
defaults_settings = GeotribuDefaults()

# ############################################################################
# ########## FUNCTIONS ###########
# ################################


def format_output_result(
    results: list[Comment], format_type: str = None, count: int = 5
) -> str:
    """Format result according to output option.

    Args:
        results: result to format
        format_type: format output option. Defaults to None.
        count: default number of results to display. Defaults to 5.

    Returns:
        formatted result ready to print
    """

    if format_type == "table":
        table = Table(
            title=f"Derniers commentaires publiés - {count}/{len(results)} résultats "
            f"\n(ctrl+clic sur le numéro pour ouvrir dans le navigateur)",
            show_lines=True,
            highlight=True,
            caption=f"{__title__} {__version__}",
        )

        # columns
        table.add_column(header="#", justify="center")
        table.add_column(header="Date", justify="center")
        table.add_column(header="Auteur/e", justify="left", style="default")
        table.add_column(header="Contenu", justify="center", style="magenta")
        table.add_column(header="Réponse à", justify="center")
        table.add_column(header="Commentaire", justify="center")

        # iterate over results

        for r in results[:count]:
            # add row
            table.add_row(
                f"[link={r.url_to_comment}]{r.id}[/link]",
                f"{r.created_as_datetime:%d %B %Y \nà %H:%m}",
                r.author,
                f"[link={r.url_to_comment}]{r.uri}[/link]",
                str(r.parent),
                r.markdownified_text,
            )

        return table
    else:
        return results


def get_latest_comments(
    number: int = 5,
    sort_by: Literal[
        "author_asc", "author_desc", "created_asc", "created_desc"
    ] = "created_asc",
    expiration_rotating_hours: int = 1,
) -> list[Comment]:
    """Download and parse latest comments published.

    Args:
        number: count of comments to download. Must be > 1. Defaults to 5.
        sort_by: comments sorting criteria. Defaults to "created_asc".
        expiration_rotating_hours (int, optional): number in hours to consider the \
            local file outdated. Defaults to 1.

    Returns:
        list of comments objects
    """
    # check if count is acceptable
    if number < 1:
        number = 1

    # download remote latest comments
    comments_file = download_remote_file_to_local(
        remote_url_to_download=f"{defaults_settings.comments_base_url}latest?limit={number}",
        local_file_path=defaults_settings.geotribu_working_folder.joinpath(
            "comments/latest.json"
        ),
        expiration_rotating_hours=expiration_rotating_hours,
        content_type="application/json",
    )

    with comments_file.open(mode="r", encoding="UTF-8") as f:
        comments = json.loads(f.read())

    li_comments = [Comment(**c) for c in comments]

    # only one comment or less? no need to sort
    if len(li_comments) < 2:
        return li_comments

    # sort
    if sort_by == "author_asc":
        return sorted(
            li_comments,
            key=lambda x: x.author,
        )
    elif sort_by == "author_desc":
        return sorted(
            li_comments,
            key=lambda x: x.author,
            reverse=True,
        )
    elif sort_by == "created_asc":
        return sorted(
            li_comments,
            key=lambda x: x.created,
        )
    elif sort_by == "created_desc":
        return sorted(
            li_comments,
            key=lambda x: x.created,
            reverse=True,
        )
    else:
        return li_comments


# ############################################################################
# ########## CLI #################
# ################################


def parser_comments_latest(
    subparser: argparse.ArgumentParser,
) -> argparse.ArgumentParser:
    """Set the argument parser for subcommand.

    Args:
        subparser (argparse.ArgumentParser): parser to set up

    Returns:
        argparse.ArgumentParser: parser ready to use
    """

    subparser.add_argument(
        "-n",
        "--results-number",
        default=getenv("GEOTRIBU_RESULTATS_NOMBRE", 5),
        help="Nombre de commentaires à retourner.",
        dest="results_number",
        metavar="GEOTRIBU_RESULTATS_NOMBRE",
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
        "-x",
        "--expiration-rotating-hours",
        help="Nombre d'heures à partir duquel considérer le fichier local comme périmé.",
        default=1,
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

    Open result of a previous command.

    Args:
        args (argparse.Namespace): arguments passed to the subcommand
    """
    logger.debug(f"Running {args.command} with {args}")

    try:
        latest_comments = get_latest_comments(
            number=args.results_number,
            sort_by="created_desc",
            expiration_rotating_hours=args.expiration_rotating_hours,
        )
    except Exception as err:
        logger.error(
            f"Une erreur a empêché la récupération des derniers commentaires. Trace: {err}"
        )
        sys.exit(1)

    # formatage de la sortie
    if len(latest_comments):
        print(
            format_output_result(
                results=latest_comments,
                format_type=args.format_output,
                count=args.results_number,
            )
        )
    else:
        print(":person_shrugging: Aucun commentaire trouvé")
        sys.exit(0)


# -- Stand alone execution
if __name__ == "__main__":
    pass
