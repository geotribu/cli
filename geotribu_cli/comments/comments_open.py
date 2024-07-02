#! python3  # noqa: E265

# ############################################################################
# ########## IMPORTS #############
# ################################

# standard library
import argparse
import logging
from os import getenv

from geotribu_cli.cli_results_rich_formatters import format_output_result_comments
from geotribu_cli.comments.comments_toolbelt import find_comment_by_id
from geotribu_cli.comments.mdl_comment import Comment

# package
from geotribu_cli.console import console
from geotribu_cli.constants import GeotribuDefaults
from geotribu_cli.utils.start_uri import open_uri

# ############################################################################
# ########## GLOBALS #############
# ################################

logger = logging.getLogger(__name__)
defaults_settings = GeotribuDefaults()

# ############################################################################
# ########## CLI #################
# ################################


def parser_comments_read(
    subparser: argparse.ArgumentParser,
) -> argparse.ArgumentParser:
    """Set the argument parser for subcommand.

    Args:
        subparser (argparse.ArgumentParser): parser to set up

    Returns:
        argparse.ArgumentParser: parser ready to use
    """

    subparser.add_argument(
        "-c",
        "--comment-id",
        default=None,
        dest="comment_id",
        help="Identifiant du commentaire à afficher. Par défaut, le dernier commentaire.",
        required=False,
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
        "-p",
        "--page-size",
        default=getenv("GEOTRIBU_COMMENTS_API_PAGE_SIZE", 20),
        dest="page_size",
        help="Nombre de commentaires par requêtes. Plus le commentaire est récent, plus "
        "c'est performant d'utiliser une petite page. À l'inverse, si on cherche un "
        "vieux commentaire, utiliser une grande page. Valeur par défaut : 20.",
        metavar="GEOTRIBU_COMMENTS_API_PAGE_SIZE",
        required=False,
        type=int,
    )

    subparser.add_argument(
        "-w",
        "--with",
        choices=[
            "app",
            "shell",
        ],
        default=getenv("GEOTRIBU_OPEN_WITH", "shell"),
        dest="open_with",
        help="Avec quoi ouvrir le commentaire : dans le terminal (shell) ou dans le "
        "navigateur (sous l'article). Valeur par défault : 'shell'.",
        metavar="GEOTRIBU_OPEN_WITH",
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
        comment_obj = find_comment_by_id(
            comment_id=args.comment_id,
            page_size=args.page_size,
            expiration_rotating_hours=args.expiration_rotating_hours,
        )
    except Exception as err:
        logger.error(
            f"Une erreur a empêché la récupération des commentaires. Trace: {err}"
        )

    # si le commentaire n'a pas été trouvé
    if isinstance(comment_obj, Comment):
        if args.open_with == "shell":
            console.print(
                format_output_result_comments(
                    results=[comment_obj], format_type=args.format_output, count=1
                )
            )
        else:
            open_uri(in_filepath=comment_obj.url_to_comment)

    else:
        console.print(
            f":person_shrugging: Le commentaire {args.comment_id} n'a pu être trouvé. "
            "Est-il publié et validé ?"
        )
