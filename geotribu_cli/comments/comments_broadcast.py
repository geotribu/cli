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
from geotribu_cli.comments.comments_latest import get_latest_comments
from geotribu_cli.constants import GeotribuDefaults
from geotribu_cli.social.mastodon_client import broadcast_to_mastodon
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
# ########## FUNCTIONS ###########
# ################################


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
        "-t",
        "--to",
        choices=[
            "mastodon",
        ],
        dest="broadcast_to",
        help="Canaux (réseaux sociaux) où publier le(s) commentaire(s).",
        required=True,
    )

    subparser.add_argument(
        "--no-auto-open",
        "--stay",
        default=str2bool(getenv("GEOTRIBU_AUTO_OPEN_AFTER", True)),
        action="store_false",
        dest="opt_auto_open_disabled",
        help="Désactive l'ouverture automatique du post à la fin de la commande.",
    )

    subparser.add_argument(
        "--no-public",
        "--private",
        default=True,
        action="store_false",
        dest="opt_no_public",
        help="Publie le commentaire en mode privé (ne fonctionne pas avec tous les "
        "canaux de diffusion).",
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
        latest_comment = get_latest_comments(
            number=5, sort_by="created_desc", expiration_rotating_hours=1
        )
        if not len(latest_comment):
            print(":person_shrugging: Aucun commentaire trouvé")
            sys.exit(0)
        latest_comment = latest_comment[0]
    except Exception as err:
        logger.error(
            "Une erreur a empêché la récupération des derniers commentaires. "
            f"Trace: {err}"
        )
        sys.exit(err)

    # check credentials
    if args.broadcast_to == "mastodon":
        try:
            online_post = broadcast_to_mastodon(
                in_comment=latest_comment, public=args.opt_no_public
            )
        except Exception as err:
            logger.error(
                f"La publication du commentaire {latest_comment.id} a échoué. "
                f"Trace : {err}"
            )
            sys.exit(1)

    print(
        f":white_check_mark: :left_speech_bubble: Commentaire {latest_comment.id}"
        f" {'déjà publié précédemment' if online_post.get('cli_newly_posted') is False else 'publié'}"
        f" sur {args.broadcast_to.title()} : {online_post.get('url')}"
    )

    # open a result
    if args.opt_auto_open_disabled:
        open_uri(in_filepath=online_post.get("url"))


# -- Stand alone execution
if __name__ == "__main__":
    pass
