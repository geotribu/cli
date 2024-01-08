#! python3  # noqa: E265

# ############################################################################
# ########## IMPORTS #############
# ################################

# standard library
import json
import logging
from typing import Literal, Optional

# package
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


def find_comment_by_id(comment_id: int) -> Optional[Comment]:
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


def get_latest_comments(
    number: int = 5,
    sort_by: Literal[
        "author_asc", "author_desc", "created_asc", "created_desc"
    ] = "created_asc",
    expiration_rotating_hours: int = 1,
    attempt: int = 1,
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

    try:
        with comments_file.open(mode="r", encoding="UTF-8") as f:
            comments = json.loads(f.read())
    except json.decoder.JSONDecodeError as err:
        logger.error(f"Impossible de lire le fichier des commentaires. Trace {err}")
        if attempt < 2:
            logger.info("Deuxième essai en forçant le téléchargement du fichier.")
            return get_latest_comments(
                number=number, sort_by=sort_by, expiration_rotating_hours=0, attempt=2
            )
        raise err

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
