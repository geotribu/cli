#! python3  # noqa: E265

# ############################################################################
# ########## IMPORTS #############
# ################################

# standard library
import csv
import json
import logging
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from os import getenv
from pathlib import Path
from textwrap import shorten
from urllib import request

# 3rd party
from rich import print

# package
from geotribu_cli.__about__ import __title_clean__, __version__
from geotribu_cli.comments.mdl_comment import Comment
from geotribu_cli.console import console
from geotribu_cli.constants import GeotribuDefaults
from geotribu_cli.rss.mdl_rss import RssItem
from geotribu_cli.utils.file_downloader import download_remote_file_to_local
from geotribu_cli.utils.formatters import convert_octets

# ############################################################################
# ########## GLOBALS #############
# ################################

logger = logging.getLogger(__name__)
defaults_settings = GeotribuDefaults()

path_local_mastodon_rss = defaults_settings.geotribu_working_folder.joinpath(
    "rss/mastodon.xml"
)
path_local_matrix_comments_toots = defaults_settings.geotribu_working_folder.joinpath(
    "comments/matrix_mastodon.keep.csv"
)
status_mastodon_tmpl = """🗨️ :geotribu: Nouveau commentaire de {author} :

{text}

Poursuivre la discussion : {url_to_comment}.

\n#Geotribot #commentaire comment-{id}"""

url_remote_mastodon_rss = f"{defaults_settings.mastodon_base_url}users/geotribu.rss"

# ############################################################################
# ########## FUNCTIONS ###########
# ################################


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
        print(in_comment.parent)
        if (
            isinstance(comment_parent_broadcasted, dict)
            and "id" in comment_parent_broadcasted
        ):
            print(
                f"Le commentaire parent {in_comment.parent} a été posté précédemment sur "
                f"Mastodon : {comment_parent_broadcasted.get('url')}. Le commentaire "
                "actuel sera donc posté en réponse."
            )
            request_data["in_reply_to_id"] = comment_parent_broadcasted.get("id")
        else:
            print(
                f"Le commentaire parent {in_comment.parent} n'a pas été posté "
                f"précédemment sur Mastodon. Le commentaire actuel ({in_comment.id}) "
                "sera donc posté comme nouveau fil de discussion."
            )

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

    {
        "User-Agent": f"{__title_clean__}/{__version__}",
        "Content-Length": len(json_data_bytes),
        "Content-Type": "application/json; charset=utf-8",
    }

    # req = request.Request(
    #     f"{defaults_settings.mastodon_base_url}api/v1/statuses",
    #     method="POST",
    #     headers=headers,
    # )

    # # install custom processor to handle 401 responses
    # opener = request.build_opener(BetterHTTPErrorProcessor)
    # request.install_opener(opener)
    # with request.urlopen(url=req, data=json_data_bytes) as response:
    #     try:
    #         content = json.loads(response.read().decode("utf-8"))
    #     except Exception as err:
    #         logger.warning(f"L'objet réponse ne semble pas être un JSON valide : {err}")
    #         content = response.read().decode("utf-8")

    # if isinstance(content, dict) and "error" in content:
    #     raise HTTPError(
    #         url=req.full_url,
    #         code="401",
    #         msg=content,
    #         hdrs=headers,
    #         fp=None,
    #     )

    # # set comment as newly posted
    # content["cli_newly_posted"] = True

    # return content


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
            "Authorization": f"Bearer {getenv('GEOTRIBU_MASTODON_API_ACCESS_TOKEN')}",
        }
        req = request.Request(
            f"{defaults_settings.mastodon_base_url}api/v1/timelines/tag/geotribot",
            method="GET",
            headers=headers,
        )

        r = request.urlopen(url=req, data=json_data_bytes)
        content = json.loads(r.read().decode("utf-8"))
        print(content)

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
                    f"{defaults_settings.mastodon_base_url}api/v1/statuses/"
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

    logger.info(
        f"Le commentaire {comment_id} n'a pas été trouvé. "
        "Il est donc considéré comme nouveau."
    )
    return None


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


def download_user_rss() -> list[RssItem]:
    """Download and parse RSS feed from Mastodon profile.

    See: https://www.reddit.com/r/Mastodon/comments/ynb0wm/how_would_i_get_only_a_single_users_statuses_with/

    Raises:
        Exception: if RSS download failed or parsing failed.

    Returns:
        list of RSS items
    """
    # download
    with console.status("Téléchargement du flux RSS...", spinner="earth"):
        local_rss = download_remote_file_to_local(
            remote_url_to_download=url_remote_mastodon_rss,
            local_file_path=path_local_mastodon_rss,
            expiration_rotating_hours=0,
        )

    # check download or existing file
    if not isinstance(local_rss, Path):
        logger.error(
            f"Le téléchargement du fichier distant {url_remote_mastodon_rss} "
            f"ou la récupération du fichier local {path_local_mastodon_rss} a échoué."
        )
        if isinstance(local_rss, Exception):
            logger.error(local_rss)
            raise local_rss

        raise FileNotFoundError(path_local_mastodon_rss)

    logger.info(
        f"Fichier RSS local du compte Mastodon : {path_local_mastodon_rss}, "
        f"{convert_octets(path_local_mastodon_rss.stat().st_size)}"
    )

    # Parse the feed
    with console.status("Lecture du fichier local...", spinner="earth"):
        feed = ET.parse(path_local_mastodon_rss)
        feed_items: list[RssItem] = []

        # Find all articles in the feed
        for item in feed.findall(".//item"):
            try:
                # add items to the feed
                feed_items.append(
                    RssItem(
                        abstract=item.find("description").text,
                        categories=[cat.text for cat in item.findall("category")],
                        date_pub=parsedate_to_datetime(item.find("pubDate").text),
                        guid=item.find("guid").text,
                        url=item.find("link").text,
                    )
                )
            except Exception as err:
                err_msg = (
                    f"L'élément {item.find('guid')} provoque une erreur à la lecture du "
                    f"fichier RSS. Trace: {err}"
                )
                logger.error(err_msg)
                continue

    return feed_items


def download_user_toots():
    # prepare search request
    request_data = {
        "exclude_replies": True,
        "limit": 40,
        "tagged": "geotribot",
    }

    json_data = json.dumps(request_data)
    json_data_bytes = json_data.encode("utf-8")  # needs to be bytes

    headers = {
        "User-Agent": f"{__title_clean__}/{__version__}",
        "Content-Length": len(json_data_bytes),
        "Content-Type": "application/json; charset=utf-8",
        # "Authorization": f"Bearer {getenv('GEOTRIBU_MASTODON_API_ACCESS_TOKEN')}",
    }
    req = request.Request(
        f"{defaults_settings.mastodon_base_url}api/v1/accounts/"
        f"{getenv('GEOTRIBU_MASTODON_API_ACCOUNT_ID', defaults_settings.mastodon_user_id)}/"
        "statuses",
        method="GET",
        headers=headers,
    )
    r = request.urlopen(url=req, data=json_data_bytes)

    try:
        print(type(r), r.getheaders(), type(r.getheader("Link")))
        content = json.loads(r.read().decode("utf-8"))
    except Exception as err:
        logger.error(
            "Impossible de récupérer les toots du compte Geotribu. "
            f"Requête : {req.full_url} {req.data}. Trace : {err}"
        )
        content = []

    return content


def write_matrix_comment_posts():
    # crée le(s) dossier(s) parent(s)
    path_local_matrix_comments_toots.parent.mkdir(parents=True, exist_ok=True)

    with path_local_matrix_comments_toots.open(mode="w", encoding="UTF-8") as csvfile:
        colonnes = ["comment_id", "comment_parent_id", "toot_id", "toot_parent_id"]
        writer = csv.DictWriter(csvfile, fieldnames=colonnes)

        writer.writeheader()


download_user_toots()
# download_user_rss()
