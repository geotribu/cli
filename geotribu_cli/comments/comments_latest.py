#! python3  # noqa: E265

# ############################################################################
# ########## IMPORTS #############
# ################################

# standard library
import argparse
import logging
import sys
from os import getenv

# 3rd party
from rich import print

# package
from geotribu_cli.cli_results_rich_formatters import format_output_result_comments
from geotribu_cli.comments.comments_toolbelt import get_latest_comments
from geotribu_cli.constants import GeotribuDefaults

# ############################################################################
# ########## GLOBALS #############
# ################################

logger = logging.getLogger(__name__)
defaults_settings = GeotribuDefaults()

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
        default=getenv("GEOTRIBU_COMMENTS_EXPIRATION_HOURS", 4),
        dest="expiration_rotating_hours",
        help="Nombre d'heures à partir duquel considérer le fichier local comme périmé.",
        type=int,
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
            format_output_result_comments(
                results=latest_comments,
                format_type=args.format_output,
                count=args.results_number,
            )
        )
    else:
        print(":person_shrugging: Aucun commentaire trouvé")
        sys.exit(0)
