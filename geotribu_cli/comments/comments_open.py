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

# 3rd party
from rich import print

# package
from geotribu_cli.comments.comments_latest import (
    format_output_result,
    get_latest_comments,
)
from geotribu_cli.comments.mdl_comment import Comment
from geotribu_cli.constants import GeotribuDefaults

# ############################################################################
# ########## GLOBALS #############
# ################################

logger = logging.getLogger(__name__)
defaults_settings = GeotribuDefaults()

# ############################################################################
# ########## FUNCTIONS ###########
# ################################


def find_comment_by_id(comment_id: int) -> Comment | None:
    """Trouve un commentaire parmi les derniers téléchargés d'après son id.

    Args:
        comment_id: id du commentaire à trouver.

    Returns:
        le commentaire trouvé ou None s'il n'est pas présent dans le fichier des
            derniers commentaires.
    """
    comments_file = defaults_settings.geotribu_working_folder.joinpath(
        "comments/latest.json"
    )
    with comments_file.open(mode="r", encoding="UTF-8") as f:
        comments = json.loads(f.read())

    li_comments = [Comment(**c) for c in comments]

    for comment in li_comments:
        if comment.id == comment_id:
            logger.info(f"Commentaire {comment_id} trouvé.")
            return comment

    logger.info(
        f"Le commentaire {comment_id} n'a pas été trouvé parmi les {len(li_comments)} "
        "commentaires récupérés."
    )
    return None


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
        help="Identifiant du commentaire à afficher. Doit faire partie des 100 derniers. "
        "Par défaut, on publie le dernier commentaire.",
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
        default=12,
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
    comment_obj = {}
    comment_found = False

    try:
        # on récupère d'abord le premier commentaire soit pour le retourner, soit pour
        # limiter le nombre de requêtes
        latest_comment = get_latest_comments(
            number=1,
            sort_by="created_desc",
            expiration_rotating_hours=args.expiration_rotating_hours,
        )

    except Exception as err:
        logger.error(
            f"Une erreur a empêché la récupération du dernier commentaire. Trace: {err}"
        )
        sys.exit(1)

    # si c'est le dernier commentaire qui a été demandé ou si rien n'a été précisé,
    # alors on le retourne sans plus attendre
    if args.comment_id is None or args.comment_id == latest_comment[0].id:
        print(
            format_output_result(
                results=latest_comment, format_type=args.format_output, count=1
            )
        )
        sys.exit(0)

    try:
        # on récupère d'abord le premier commentaire soit pour le retourner, soit pour
        # limiter le nombre de requêtes
        latest_comment = get_latest_comments(
            number=1,
            sort_by="created_desc",
            expiration_rotating_hours=args.expiration_rotating_hours,
        )[0]

        if args.comment_id is None or 0:
            comment_found = True
            comment_obj = latest_comment

        api_request_page_size = args.page_size
        # doit être à 0 si le com' n'est pas trouvé dans le fichier local pour forcer le téléchargement incrémental
        local_expiration_delay_hours = args.expiration_rotating_hours

        while all(
            [comment_found is False, api_request_page_size <= int(latest_comment.id)]
        ):
            published_comments = get_latest_comments(
                number=api_request_page_size,
                sort_by="created_desc",
                expiration_rotating_hours=local_expiration_delay_hours,
            )

            if not len(published_comments):
                print(":person_shrugging: Aucun commentaire trouvé")
                sys.exit(0)

            comment_obj = find_comment_by_id(comment_id=args.comment_id)

            if isinstance(comment_obj, Comment):
                comment_found = True
                break
            else:
                logger.debug(
                    f"Le commentaire {args.comment_id} n'a pas été trouvé parmi les "
                    f"{api_request_page_size} derniers commentaires. Nouvelle requête "
                    f"pour chercher parmi les {api_request_page_size*2} derniers commentaires..."
                )
                api_request_page_size = api_request_page_size * 2
                local_expiration_delay_hours = 0
    except Exception as err:
        logger.error(
            f"Une erreur a empêché la récupération des commentaires. Trace: {err}"
        )
        sys.exit(1)

    # si le commentaire n'a pas été trouvé
    if not isinstance(comment_obj, Comment):
        print(
            f":person_shrugging: Le commentaire {args.comment_id} n'a pu être trouvé. "
            "Est-il publié et validé ?"
        )
        sys.exit(0)

    print(
        format_output_result(
            results=[comment_obj], format_type=args.format_output, count=1
        )
    )
    sys.exit(0)


# -- Stand alone execution
if __name__ == "__main__":
    pass
