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


def filter_comment_by_id(comment_id: int) -> Optional[Comment]:
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


def find_comment_by_id(
    comment_id: int,
    page_size: int = 20,
    expiration_rotating_hours: int = 1,
) -> Optional[Comment]:
    """Trouve un commentaire parmi tout ceux publiés à partir de son identifiant.

    Args:
        comment_id: identifiant du commentaire
        page_size: nombre de commentaires par requêtes. Plus le commentaire est récent,
            plus c'est performant d'utiliser une petite page. À l'inverse, si on
            cherche un 'vieux' commentaire, mieux vaut utiliser une grande page.
            Defaults to 20.
        expiration_rotating_hours: Nombre d'heures à partir duquel considérer le
            fichier local comme périmé.. Defaults to 1.

    Raises:
        err: si une erreur se produit pendant la récupération des commentaires

    Returns:
        le commentaire s'il a été trouvé ou None le cas échéant
    """
    # local vars
    comment_obj = None
    comment_found = False

    try:
        # on récupère d'abord le premier commentaire soit pour le retourner, soit pour
        # limiter le nombre de requêtes
        latest_comment = get_latest_comments(
            number=1,
            sort_by="created_desc",
            expiration_rotating_hours=expiration_rotating_hours,
        )
        logger.debug(f"Dernier commentaire récupéré {latest_comment[0].id}.")
    except Exception as err:
        logger.error(
            f"Une erreur a empêché la récupération du dernier commentaire. Trace: {err}"
        )
        raise err

    # si c'est le dernier commentaire qui a été demandé ou si rien n'a été précisé,
    # alors on le retourne sans plus attendre
    if comment_id is None or comment_id == int(latest_comment[0].id):
        logger.info(
            f"Le dernier commentaire récupéré {latest_comment[0].id} correspond à celui "
            "demandé. Voilà qui va nous faire gagner du temps, quelle chance !"
        )
        return latest_comment[0]

    # sinon on se prépare à itérer sur la récupération des commentaires avec une montée
    # en puissance progressive et limitée à l'identifiant le plus récent
    try:
        api_request_page_size = page_size
        max_page_size_reached = 0
        # doit être à 0 si le com' n'est pas trouvé dans le fichier local pour forcer le téléchargement incrémental
        local_expiration_delay_hours = expiration_rotating_hours

        while all(
            [
                comment_found is False,
                api_request_page_size <= int(latest_comment[0].id),
                max_page_size_reached < 2,
            ]
        ):
            published_comments = get_latest_comments(
                number=api_request_page_size,
                sort_by="created_desc",
                expiration_rotating_hours=local_expiration_delay_hours,
            )

            if not len(published_comments):
                logger.warning("Aucun commentaire trouvé")
                return None

            # parcourir les résultats pour voir si le commentaire n'y est pas
            comment_obj = filter_comment_by_id(comment_id=comment_id)

            if isinstance(comment_obj, Comment):
                comment_found = True
                break
            else:
                api_request_page_size = api_request_page_size * 2
                # Vérifier si la variable dépasse le plafond
                if (
                    api_request_page_size > int(latest_comment[0].id)
                    and not max_page_size_reached
                ):
                    api_request_page_size = int(latest_comment[0].id)
                    # ainsi à la prochaine itération, on sort de la boucle
                    max_page_size_reached += 1

                local_expiration_delay_hours = 0
                logger.debug(
                    f"Le commentaire {comment_id} n'a pas été trouvé parmi les "
                    f"{api_request_page_size} derniers commentaires. Nouvelle requête "
                    f"pour chercher parmi les {api_request_page_size} derniers commentaires..."
                )
    except Exception as err:
        logger.error(
            f"Une erreur a empêché la récupération des commentaires. Trace: {err}"
        )
        raise err

    return comment_obj


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
