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
from textwrap import shorten
from urllib import request

# 3rd party
from markdownify import markdownify
from rich import print

# package
from geotribu_cli.__about__ import __title_clean__, __version__
from geotribu_cli.constants import Comment, GeotribuDefaults
from geotribu_cli.subcommands.comments_latest import get_latest_comments

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


def comment_to_media(in_comment: Comment, media: str) -> str:
    """Format comment to fit media size and publication rules.

    Args:
        in_comment: comment to format
        media: name of the targetted media

    Returns:
        formatted comment
    """
    if media == "mastodon":
        logger.info(f"Formatting comment {in_comment.id} for {media}")
        # 500 caractères - longueur du template = 370
        max_text_length = (
            370 - len(in_comment.author) - len(str(in_comment.id)) - 4
        )  # 4 = placeholder final

        return status_mastodon_tmpl.format(
            author=in_comment.author,
            url_to_comment=in_comment.url_to_comment,
            text=shorten(markdownify(in_comment.text), width=max_text_length),
            id=in_comment.id,
        )


def broadcast_to_mastodon(in_comment: Comment, public: bool = True) -> dict:
    """Post the latest comment to Mastodon.

    Args:
        in_comment: comment to broadcast
        public: if not, the comment is sent as direct message, so it's not public.

    Returns:
        URL to posted status
    """
    if getenv("GEOTRIBU_MASTODON_API_ACCESS_TOKEN") is None:
        logger.error(
            "Le jeton d'accès à l'API Mastodon n'a pas été trouvé en variable "
            "d'environnement GEOTRIBU_MASTODON_API_ACCESS_TOKEN. "
            "Le récupérer depuis : https://mapstodon.space/settings/applications/7909"
        )
        return None

    # prepare status
    request_data = {
        "status": comment_to_media(in_comment=in_comment, media="mastodon"),
        "language": "fr",
    }
    if not public:
        logger.debug("Comment will be posted as direct message.")
        request_data["visibility"] = "direct"

    json_data = json.dumps(request_data)
    json_data_bytes = json_data.encode("utf-8")  # needs to be bytes

    headers = {
        "User-Agent": f"{__title_clean__}/{__version__}",
        "Content-Length": len(json_data_bytes),
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {getenv('GEOTRIBU_MASTODON_API_ACCESS_TOKEN')}",
    }
    req = request.Request(
        f"{defaults_settings.mastodon_base_url}/api/v1/statuses",
        method="POST",
        headers=headers,
    )

    r = request.urlopen(url=req, data=json_data_bytes)
    content = json.loads(r.read().decode("utf-8"))
    return content.get("uri")


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
        "--no-public",
        default=True,
        action="store_false",
        dest="opt_no_public",
        help="Publie le commentaire en mode privé (ne fonctionne pas avec tous les canaux de diffusion).",
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
        latest_comment = get_latest_comments(number=1, sort_by="created_desc")
        if not len(latest_comment):
            print(":person_shrugging: Aucun commentaire trouvé")
            sys.exit(0)
        latest_comment = latest_comment[0]
    except Exception as err:
        logger.error(
            f"Une erreur a empêché la récupération des derniers commentaires. Trace: {err}"
        )
        sys.exit(1)

    # check credentials
    if args.broadcast_to == "mastodon":
        try:
            mastodon_post = broadcast_to_mastodon(in_comment=latest_comment)
        except Exception as err:
            logger.error(f"Trace : {err}")

        print(
            f":check-mark-button: Commentaire {latest_comment.id} publié sur Mastodon : {mastodon_post}"
        )


# -- Stand alone execution
if __name__ == "__main__":
    pass
