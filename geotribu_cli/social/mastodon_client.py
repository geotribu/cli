#! python3  # noqa: E265

# ############################################################################
# ########## IMPORTS #############
# ################################


# standard library
import csv
import logging
import re
from os import getenv
from pathlib import Path
from textwrap import shorten
from typing import Optional
from urllib.parse import urlparse

# 3rd party
from mastodon import Mastodon, MastodonAPIError, MastodonError
from requests import Session

# package
from geotribu_cli.__about__ import __title_clean__, __version__
from geotribu_cli.comments.mdl_comment import Comment
from geotribu_cli.constants import GeotribuDefaults

# ############################################################################
# ########## GLOBALS #############
# ################################

logger = logging.getLogger(__name__)
defaults_settings = GeotribuDefaults()

regex_pattern_comment_id = r"comment-\d{2,4}"

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
    my_statuses: Optional[list] = None

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
        """Instanciation class. Args are inherited."""
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
            elif isinstance(access_token, str) and len(access_token) < 25:
                logger.critical(
                    "Le jeton d'accès à l'API Mastodon récupéré semble incorrect "
                    f"(moins de 25 caractères): {access_token}"
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
            access_token=access_token.strip(),
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

    def broadcast_comment(
        self,
        in_comment: Comment,
    ) -> dict:
        """Post the latest comment to Mastodon.

        Args:
            in_comment: comment to broadcast

        Returns:
            URL to posted status
        """
        in_reply_to_id = None

        # check if comment has not been already published
        already_broadcasted = self.comment_already_broadcasted(comment_id=in_comment.id)
        if isinstance(already_broadcasted, dict):
            already_broadcasted["cli_newly_posted"] = False
            return already_broadcasted

        # check if parent comment has been posted
        if in_comment.parent is not None:
            comment_parent_broadcasted = self.comment_already_broadcasted(
                comment_id=in_comment.parent
            )
            if (
                isinstance(comment_parent_broadcasted, dict)
                and "id" in comment_parent_broadcasted
            ):
                logger.info(
                    f"Le commentaire parent {in_comment.parent} a déjà été posté "
                    "précédemment sur Mastodon : "
                    f"{comment_parent_broadcasted.get('url')}. Le commentaire "
                    f"{in_comment.id} actuel sera donc posté en réponse."
                )
                in_reply_to_id = comment_parent_broadcasted.get("id")
            else:
                logger.info(
                    f"Le commentaire parent {in_comment.parent} n'a été posté précédemment "
                    f"sur Mastodon. Le commentaire actuel ({in_comment.id}) sera donc "
                    "posté comme nouveau fil de discussion."
                )

        new_status = self.status_post(
            status=self.comment_to_media(in_comment=in_comment),
            in_reply_to_id=in_reply_to_id,
            language="fr",
            visibility=getenv("GEOTRIBU_MASTODON_DEFAULT_VISIBILITY", "unlisted"),
        )
        if isinstance(new_status, dict):
            new_status["cli_newly_posted"] = True

        return new_status

    def comment_already_broadcasted(self, comment_id: int) -> Optional[dict]:
        """Check if comment has already been broadcasted on the media.

        Args:
            comment_id: id of the comment to check

        Returns:
            post on media if it has been already published
        """
        # download statuses with #geotribot if not already stored in memory
        if self.my_statuses is None:
            my_statuses = self.account_statuses(
                id=self.me().get("id"),
                tagged="geotribot",
                limit=40,
                exclude_reblogs=True,
            )
            every_statuses = self.fetch_remaining(my_statuses)
            logger.debug(f"{len(every_statuses)} statuts récupérés.")
            self.my_statuses = every_statuses
        else:
            every_statuses = self.my_statuses
            logger.debug(
                f"Réutilise les {len(every_statuses)} téléchargés précédemment."
            )

        # parse every downloaded status
        for status in every_statuses:
            status_tags = status.get("tags")

            # check if status has tag (it should since the requests is already filtered...)
            if not isinstance(status_tags, list) and len(status_tags):
                logger.debug(
                    f"Exclusion de {status.get('url')} car il n'a aucun hashtag."
                )
                continue

            tags_names = [tag.get("name") for tag in status_tags]

            # check if status has the two required tags
            if "geotribot" not in tags_names and "commentaire" not in tags_names:
                logger.debug(
                    f"Exclusion de {status.get('url')} car il ne contient pas les deux "
                    "hashtags requis : #geotribot ET #commentaire."
                )
                continue

            # check if status has a comment-id
            matches = re.findall(regex_pattern_comment_id, status.get("content"))
            if not len(matches):
                logger.debug(
                    f"Exclusion de {status.get('url')} car il ne contient pas "
                    "d'identifiant de commentaire."
                )
                continue
            logger.debug(
                f"Le statut {status.get('url')} correspond au commentaire : "
                f"{matches[0].removeprefix('comment-')}"
            )

            try:
                status_comment_id = int(matches[0].removeprefix("comment-"))
                if status_comment_id == comment_id:
                    logger.info(
                        f"Le commentaire {comment_id} a déjà été publié sur Mastodon : "
                        f"{status.get('url')}"
                    )
                    return status
            except ValueError as err:
                logger.error(f"Converting comment-id into integer failed. Trace: {err}")

        logger.info(
            f"Le commentaire {comment_id} n'a pas été trouvé sur Mastodon. "
            "Il est donc considéré comme nouveau."
        )

        return None

    def comment_to_media(self, in_comment: Comment) -> str:
        """Format comment to fit media size and publication rules.

        Args:
            in_comment: comment to format


        Returns:
            formatted comment
        """

        logger.debug(f"Formatting comment {in_comment.id}")
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
                    liste.get("title"): self.fetch_remaining(
                        self.list_accounts(id=liste.get("id"))
                    )
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
                masto_following_accounts = self.fetch_remaining(
                    self.account_following(id=self.me())
                )
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


# Stand alone execution
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    mastodon_client = ExtendedMastodonClient()
    mastodon_client.comment_already_broadcasted(321)
