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
from geotribu_cli.comments.comments_toolbelt import find_comment_by_id
from geotribu_cli.comments.mdl_comment import Comment
from geotribu_cli.constants import GeotribuDefaults
from geotribu_cli.social.mastodon_client import (  # broadcast_to_mastodon,
    ExtendedMastodonClient,
)
from geotribu_cli.utils.start_uri import open_uri
from geotribu_cli.utils.str2bool import str2bool

# ############################################################################
# ########## GLOBALS #############
# ################################

logger = logging.getLogger(__name__)
defaults_settings = GeotribuDefaults()


status_mastodon_tmpl = """🗨️ :geotribu: Nouveau commentaire de {author} :

{text}

Poursuivre la discussion : {url_to_comment}.

\n#Geotribot #commentaire comment-{id}"""


# ############################################################################
# ########## CLI #################
# ################################


def parser_comments_broadcast(
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
        "-t",
        "--to",
        choices=[
            "mastodon",
        ],
        default="mastodon",
        dest="broadcast_to",
        help="Canaux (réseaux sociaux) où publier le(s) commentaire(s).",
        required=True,
    )

    subparser.add_argument(
        "-x",
        "--expiration-rotating-hours",
        default=getenv("GEOTRIBU_COMMENTS_EXPIRATION_HOURS", 4),
        dest="expiration_rotating_hours",
        help="Nombre d'heures à partir duquel considérer le fichier local comme périmé.",
        type=int,
    )

    subparser.add_argument(
        "--no-auto-open",
        "--stay",
        default=str2bool(getenv("GEOTRIBU_AUTO_OPEN_AFTER", True)),
        action="store_false",
        dest="opt_auto_open_disabled",
        help="Désactive l'ouverture automatique du post à la fin de la commande.",
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

    # get latest comment
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
        sys.exit(1)

    # si le commentaire n'a pas été trouvé
    if not isinstance(comment_obj, Comment):
        print(
            f":person_shrugging: Le commentaire {args.comment_id} n'a pu être trouvé. "
            "Est-il publié et validé ?"
        )
        sys.exit(0)

    # check credentials
    if args.broadcast_to == "mastodon":
        try:
            mastodon_client = ExtendedMastodonClient()
            online_post = mastodon_client.broadcast_comment(in_comment=comment_obj)
            if not online_post:
                print(f"le commentaire n'a pas encore été publié : {comment_obj.id}")
        except Exception as err:
            logger.error(
                f"La publication du commentaire {comment_obj.id} a échoué. "
                f"Trace : {err}"
            )
            sys.exit(1)

    print(
        f":white_check_mark: :left_speech_bubble: Commentaire {comment_obj.id}"
        f" {'déjà publié précédemment' if online_post.get('cli_newly_posted') is False else 'publié'}"
        f" sur {args.broadcast_to.title()} : {online_post.get('url')}"
    )

    # open a result
    if args.opt_auto_open_disabled:
        open_uri(in_filepath=online_post.get("url"))
