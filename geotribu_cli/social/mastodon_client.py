#! python3  # noqa: E265

# ############################################################################
# ########## IMPORTS #############
# ################################


# standard library
import csv
import json
import logging
from os import getenv
from pathlib import Path
from textwrap import shorten
from typing import Optional
from urllib import request
from urllib.parse import urlparse

# 3rd party
from mastodon import Mastodon, MastodonAPIError, MastodonError
from requests import Session
from rich import print

# package
from geotribu_cli.__about__ import __title_clean__, __version__
from geotribu_cli.comments.mdl_comment import Comment
from geotribu_cli.constants import GeotribuDefaults
from geotribu_cli.utils.proxies import get_proxy_settings

# ############################################################################
# ########## GLOBALS #############
# ################################

logger = logging.getLogger(__name__)
defaults_settings = GeotribuDefaults()


status_mastodon_tmpl = """🗨️ :geotribu: Nouveau commentaire de {author} :

{text}

Poursuivre la discussion : {url_to_comment}.

\n#Geotribot #commentaire comment-{id}"""

# CSV output
default_dest_path_following_accounts = (
    defaults_settings.geotribu_working_folder.joinpath(
        "mastodon/export/mastodon_comptes_suivis_geotribu.csv"
    )
)
default_dest_path_lists = defaults_settings.geotribu_working_folder.joinpath(
    "mastodon/export/mastodon_listes_geotribu.csv"
)
default_dest_path_lists_only_accounts = (
    defaults_settings.geotribu_working_folder.joinpath(
        "mastodon/export/mastodon_comptes_des_listes_geotribu"
    )
)

# ############################################################################
# ########## CLASSES #############
# ################################


class ExtendedMastodonClient(Mastodon):
    """Extended Mastodon client with custom methods and attributes.

    Raises:
        MastodonError: if access token is not set
    """

    csv_accounts_columns_names = [
        "Account address",
        "Show boosts",
        "Notify on new posts",
        "Languages",
    ]

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        api_base_url: str = defaults_settings.mastodon_base_url,
        debug_requests: Optional[bool] = None,
        ratelimit_method: str = "wait",
        ratelimit_pacefactor: float = 1.1,
        request_timeout: int = 60,
        mastodon_version: Optional[str] = None,
        version_check_mode: str = "created",
        session: Optional[Session] = None,
        feature_set: str = "mainline",
        user_agent: str = f"{__title_clean__}/{__version__}",
        lang: Optional[str] = "fra",
    ):
        # handle some attributes
        if access_token is None:
            access_token = getenv("GEOTRIBU_MASTODON_API_ACCESS_TOKEN")
            if access_token is None:
                logger.critical(
                    "Le jeton d'accès à l'API Mastodon n'a pas été trouvé en variable "
                    "d'environnement GEOTRIBU_MASTODON_API_ACCESS_TOKEN. "
                    "Le récupérer depuis : https://mapstodon.space/settings/applications/7909"
                )
                raise MastodonError(
                    f"Le jeton d'accès à l'API Mastodon (instance : {api_base_url}) est requis."
                )

        if debug_requests is None:
            debug_requests = getenv("GEOTRIBU_LOGS_LEVEL", "") == "DEBUG"

        # instanciate subclass
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            access_token=access_token,
            api_base_url=api_base_url,
            debug_requests=debug_requests,
            ratelimit_method=ratelimit_method,
            ratelimit_pacefactor=ratelimit_pacefactor,
            request_timeout=request_timeout,
            mastodon_version=mastodon_version,
            version_check_mode=version_check_mode,
            session=session,
            feature_set=feature_set,
            user_agent=user_agent,
            lang=lang,
        )

    @classmethod
    def full_account_with_instance(
        cls, account: dict, default_instance: str = "mapstodon.space"
    ):
        """Make sure the account contains instance domain.

        Args:
            default_instance: default instance domain. Defaults to mapstodon.space.
            account: account dictionary

        Returns:
            account with default instance if not present

        Example:

        .. code-block:: python

        >>> print(ExtendedMastodonClient.full_account_with_instance(account={"acct": "datagouvfr@social.numerique.gouv.fr"}))
        datagouvfr@social.numerique.gouv.fr
        >>> print(ExtendedMastodonClient.full_account_with_instance(account={"acct": "leaflet"}))
        leaflet@mapstodon.space
        >>> print(ExtendedMastodonClient.full_account_with_instance(account={"acct": "opengisch"}, default_instance="fosstodon.org))
        opengisch@fosstodon.org

        """
        member_account_full: str = account.get("acct")
        if "@" not in member_account_full:
            member_account_full = f"{member_account_full}@{default_instance}"
        return member_account_full

    @classmethod
    def url_to_instance_domain(cls, url: str) -> str:
        """Extract instance domain from URL.

        Args:
            url: input URL

        Returns:
            instance domain

        Example:

        .. code-block:: python

        >>> print(ExtendedMastodonClient.url_to_instance_domain(url="https://mapstodon.space/@geotribu"))
        mapstodon.space

        """
        parsed_url = urlparse(url)
        return parsed_url.netloc

    def export_data(
        self,
        dest_path_following_accounts: Optional[
            Path
        ] = default_dest_path_following_accounts,
        dest_path_lists: Optional[Path] = default_dest_path_lists,
        dest_path_lists_only_accounts: Optional[
            Path
        ] = default_dest_path_lists_only_accounts,
    ) -> tuple[Optional[Path], Optional[Path], Optional[Path]]:
        """Export account data.

        Args:
            dest_path_following_accounts: path to the CSV file for following accounts
                export. Defaults to default_dest_path_following_accounts.
            dest_path_lists: path to the CSV file for lists export. Defaults to
                default_dest_path_lists.
            dest_path_lists_only_accounts: path to the CSV file for only accounts from
                lists export. Defaults to default_dest_path_lists_only_accounts.

        Raises:
            MastodonAPIError: when it's impossible to perform API request for profile
                information.

        Returns:
            tuple of paths of exported files
        """
        # check si au moins un export est défini
        if not any(
            [
                dest_path_following_accounts,
                dest_path_lists,
                dest_path_lists_only_accounts,
            ]
        ):
            logger.debug("Aucun format d'export spécifié. Abandon.")
            return (None, None, None)

        # -- Récupération des éléments à exporter auprès de l'API --
        try:
            mastodon_profile = self.me()
            default_instance_domain = self.url_to_instance_domain(
                url=mastodon_profile.get("url")
            )
        except Exception as err:
            logger.critical(
                "La récupération du profil auprès de l'API a échoué. L'export est "
                f"impossible. Trace: {err}"
            )
            raise MastodonAPIError(
                "Impossible de récupérer les informations du profil."
            )

        # récupération des listes
        if dest_path_lists is not None or dest_path_lists_only_accounts is not None:
            try:
                dico_listes = {
                    liste.get("title"): self.list_accounts(id=liste.get("id"))
                    for liste in self.lists()
                }
            except Exception as err:
                logger.critical(
                    "La récupération des listes a échoué. L'export est "
                    f"impossible. Trace: {err}"
                )
                dest_path_lists = dest_path_lists_only_accounts = None

        # récupération des comptes suivis
        if dest_path_following_accounts is not None:
            try:
                masto_following_accounts = self.account_following(id=self.me())
            except Exception as err:
                logger.critical(
                    "La récupération des comptes suivis a échoué. L'export est "
                    f"impossible. Trace: {err}"
                )
                dest_path_following_accounts = None

        # -- Export --
        if dest_path_lists:
            dest_path_lists = self.export_lists(
                mastodon_lists=dico_listes,
                dest_csv_path=dest_path_lists,
                default_instance=default_instance_domain,
            )

        if dest_path_lists_only_accounts:
            dest_path_lists_only_accounts = self.export_accounts(
                mastodon_accounts=[
                    account_from_list
                    for liste in dico_listes.values()
                    for account_from_list in liste
                ],
                dest_csv_path=dest_path_lists_only_accounts,
                default_instance=default_instance_domain,
            )

        if dest_path_following_accounts:
            dest_path_following_accounts = self.export_accounts(
                mastodon_accounts=masto_following_accounts,
                dest_csv_path=dest_path_following_accounts,
                default_instance=default_instance_domain,
            )

        return (
            dest_path_following_accounts,
            dest_path_lists,
            dest_path_lists_only_accounts,
        )

    def export_accounts(
        self,
        mastodon_accounts: list[dict],
        dest_csv_path: Path = default_dest_path_following_accounts,
        default_instance: str = "mapstodon.space",
    ) -> Path:
        """Export Mastodon following accounts into CSV file as web UI.

        Args:
            mastodon_accounts: list of accounts
            dest_csv_path: path to the CSV file to write to. Defaults to
                default_dest_path_following_accounts.
            default_instance: default instance domain when account is on the same.
                Defaults to mapstodon.space.

        Returns:
            path to the CSV file
        """
        dest_csv_path.parent.mkdir(parents=True, exist_ok=True)
        with dest_csv_path.open(
            mode="w", newline="", encoding="utf-8"
        ) as out_csv_following_accounts:
            # générateurs de CSV
            csv_writer_following_accounts = csv.writer(out_csv_following_accounts)
            # en-tête (colonnes de la première ligne)
            csv_writer_following_accounts.writerow(self.csv_accounts_columns_names)

            for following in mastodon_accounts:
                member_account_full = self.full_account_with_instance(
                    account=following,
                    default_instance=default_instance,
                )

                # et zou, dans les CSV
                csv_writer_following_accounts.writerow(
                    (member_account_full, "true", "false", "")
                )

        logger.info(f"L'export des comptes a réussi: {dest_csv_path.resolve()}.")
        return dest_csv_path

    def export_lists(
        self,
        mastodon_lists: dict[str, list[dict]],
        dest_csv_path: Path = default_dest_path_lists,
        default_instance: str = "mapstodon.space",
    ) -> Path:
        """Export lists.

        Args:
            mastodon_lists: _description_
            dest_csv_path: path to the CSV file to write to. Defaults to
                default_dest_path_following_accounts.
            default_instance: default instance domain when account is on the same.
                Defaults to mapstodon.space.

        Returns:
            path to the CSV file
        """
        dest_csv_path.parent.mkdir(parents=True, exist_ok=True)

        with dest_csv_path.open(
            mode="w", encoding="utf-8", newline=""
        ) as out_csv_lists:
            csv_writer_lists = csv.writer(out_csv_lists)

            # on parcourt les listes du compte authentifié
            for liste, members in mastodon_lists.items():
                # on parcourt la liste en la triant sur le nom du compte pour faciliter
                # d'éventuelles comparaisons à l'oeil nu ou autres
                for member in sorted(members, key=lambda x: x["acct"]):
                    # Aucune info retournée par l'API ne correspond au formaslime du module
                    # import/export de l'application web... ainsi les comptes d'une même
                    # instance n'ont pas son adresse. On gère donc cela manuellement
                    member_account_full: str = self.full_account_with_instance(
                        account=member,
                        default_instance=default_instance,
                    )

                    # et zou, dans les CSV
                    csv_writer_lists.writerow((liste, member_account_full))
        logger.info(f"L'export des listes a réussi: {dest_csv_path.resolve()}")
        return dest_csv_path


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
        if (
            isinstance(comment_parent_broadcasted, dict)
            and "id" in comment_parent_broadcasted
        ):
            print(
                f"Le commentaire parent {in_comment.parent}a été posté précédemment sur "
                f"Mastodon : {comment_parent_broadcasted.get('url')}. Le commentaire "
                "actuel sera posté en réponse."
            )
            request_data["in_reply_to_id"] = comment_parent_broadcasted.get("id")
        else:
            print(
                f"Le commentaire parent {in_comment.parent} n'a été posté précédemment "
                f"sur Mastodon. Le commentaire actuel ({in_comment.id}) sera donc posté comme nouveau fil "
                "de discussion."
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

    # json_data = json.dumps(request_data)
    # json_data_bytes = json_data.encode("utf-8")  # needs to be bytes

    headers = {
        "User-Agent": f"{__title_clean__}/{__version__}",
        # "Content-Length": len(json_data_bytes),
        # "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {getenv('GEOTRIBU_MASTODON_API_ACCESS_TOKEN')}",
    }

    with Session() as post_session:
        post_session.proxies.update(get_proxy_settings())
        post_session.headers.update(headers)

        req = post_session.post(
            url=f"{defaults_settings.mastodon_base_url}api/v1/statuses",
            json=request_data,
        )
        req.raise_for_status()

    content = req.json()

    # set comment as newly posted
    content["cli_newly_posted"] = True

    return content


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
            f"{defaults_settings.mastodon_base_url}api/v1/timelines/tag/geotribot",
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
