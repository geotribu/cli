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
from rich import print

# package
from geotribu_cli.__about__ import __title_clean__, __version__
from geotribu_cli.comments.comments_latest import get_latest_comments
from geotribu_cli.comments.mdl_comment import Comment
from geotribu_cli.constants import GeotribuDefaults
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
            text=shorten(in_comment.markdownified_text, width=max_text_length),
            id=in_comment.id,
        )


def comment_already_broadcasted(comment_id: int, media: str = "mastodon") -> dict:
    """Check if comment has already been broadcasted on the media.

    Args:
        comment_id: id of the comment to check
        media: name of the targetted media

    Returns:
        post on media if it has been already published
    """
    if media == "mastodon":
        if getenv("GEOTRIBU_MASTODON_API_ACCESS_TOKEN") is None:
            logger.error(
                "Le jeton d'accès à l'API Mastodon n'a pas été trouvé en variable "
                "d'environnement GEOTRIBU_MASTODON_API_ACCESS_TOKEN. "
                "Le récupérer depuis : https://mapstodon.space/settings/applications/7909"
            )
            return None

        # prepare search request
        request_data = {
            "all": ["commentaire"],
            "limit": 40,
            "local": True,
            "since_id": "110549835686856734",
        }

        json_data = json.dumps(request_data)
        json_data_bytes = json_data.encode("utf-8")  # needs to be bytes

        headers = {
            "User-Agent": f"{__title_clean__}/{__version__}",
            "Content-Length": len(json_data_bytes),
            "Content-Type": "application/json; charset=utf-8",
        }
        req = request.Request(
            f"{defaults_settings.mastodon_base_url}/api/v1/timelines/tag/geotribot",
            method="GET",
            headers=headers,
        )

        r = request.urlopen(url=req, data=json_data_bytes)
        content = json.loads(r.read().decode("utf-8"))

        for status in content:
            if f"comment-{comment_id}</p>" in status.get("content"):
                logger.info(
                    f"Le commentaire {comment_id} a déjà été publié sur {media} : "
                    f"{status.get('url')}"
                )
                return status
            if status.get("replies_count", 0) < 1:
                logger.debug(
                    f"Le statut {status.get('id')} n'a aucune réponse. Au suivant !"
                )
                continue
            else:
                logger.info(
                    f"Le statut {status.get('id')} a {status.get('replies_count')} "
                    "réponse(s). Cherchons parmi les réponses si le commentaire "
                    f"{comment_id} n'y est pas..."
                )
                req = request.Request(
                    f"{defaults_settings.mastodon_base_url}/api/v1/statuses/"
                    f"{status.get('id')}/context",
                    method="GET",
                    headers=headers,
                )
                r = request.urlopen(url=req, data=json_data_bytes)
                content = json.loads(r.read().decode("utf-8"))
                for reply_status in content.get("descendants", []):
                    if f"comment-{comment_id}</p>" in reply_status.get("content"):
                        print(
                            f"Le commentaire {comment_id} a déjà été publié sur {media} : "
                            f"{reply_status.get('url')}, en réponse à {status.get('id')}"
                        )
                        return reply_status

    return None


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

    # check if comment has not been already published
    already_broadcasted = comment_already_broadcasted(
        comment_id=in_comment.id, media="mastodon"
    )
    if isinstance(already_broadcasted, dict):
        already_broadcasted["cli_newly_posted"] = False
        return already_broadcasted

    # prepare status
    request_data = {
        "status": comment_to_media(in_comment=in_comment, media="mastodon"),
        "language": "fr",
    }

    # check if parent comment has been posted
    if in_comment.parent is not None:
        comment_parent_broadcasted = comment_already_broadcasted(
            comment_id=in_comment.parent, media="mastodon"
        )
        if (
            isinstance(comment_parent_broadcasted, dict)
            and "id" in comment_parent_broadcasted
        ):
            print(
                "Le commentaire parent a été posté précédemment sur Mastodon : "
                f"{comment_parent_broadcasted.get('url')}. Le commentaire actuel sera "
                "posté en réponse."
            )
            request_data["in_reply_to_id"] = comment_parent_broadcasted.get("id")

    # unlisted or direct
    if not public:
        logger.debug("Comment will be posted as DIRECT message.")
        request_data["visibility"] = "direct"
    else:
        logger.debug("Comment will be posted as UNLISTED message.")
        request_data["visibility"] = getenv(
            "GEOTRIBU_MASTODON_DEFAULT_VISIBILITY", "unlisted"
        )

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
    content["cli_newly_posted"] = True
    return content


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
        latest_comment = get_latest_comments(number=5, sort_by="created_desc")
        if not len(latest_comment):
            print(":person_shrugging: Aucun commentaire trouvé")
            sys.exit(0)
        latest_comment = latest_comment[0]
    except Exception as err:
        logger.error(
            "Une erreur a empêché la récupération des derniers commentaires. "
            f"Trace: {err}"
        )
        sys.exit(1)

    # check credentials
    if args.broadcast_to == "mastodon":
        try:
            online_post = broadcast_to_mastodon(
                in_comment=latest_comment, public=args.opt_no_public
            )
        except Exception as err:
            logger.error(f"Trace : {err}")
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
