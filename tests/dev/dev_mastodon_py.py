#! python3  # noqa: E265

# standard lib
import csv
import logging
from os import getenv
from pathlib import Path

# 3rd party
from mastodon import Mastodon

# projet
from geotribu_cli.__about__ import __title_clean__, __version__
from geotribu_cli.constants import GeotribuDefaults

defaults_settings = GeotribuDefaults()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Output CSV settings
csv_path_accounts = Path("mastodon_comptes_suivis_geotribu.csv")
csv_path_lists_only_accounts = Path("mastodon_comptes_des_listes_geotribu.csv")
csv_accounts_columns_names = [
    "Account address",
    "Show boosts",
    "Notify on new posts",
    "Languages",
]
csv_path_lists = Path("mastodon_listes_geotribu.csv")
# csv_lists_columns_names = ["List name", "Account address"] #  on this export, there is no column names


masto_client = Mastodon(
    access_token=getenv("GEOTRIBU_MASTODON_API_ACCESS_TOKEN"),
    api_base_url=f"{defaults_settings.mastodon_base_url}",
    user_agent=f"{__title_clean__}-dev/{__version__}",
)

print(masto_client.me().keys())
print(masto_client.me().get("url"))

# for liste in masto_client.lists():
#     print(liste.get("title"))
#     print(masto_client.list_accounts(id=liste.get("id"))[0].keys())
#     print(masto_client.list_accounts(id=liste.get("id"))[0].get("uri"))
#     print(masto_client.list_accounts(id=liste.get("id"))[0].get("acct"))
#     print(masto_client.list_accounts(id=liste.get("id"))[0].get("id"))
#     print(masto_client.list_accounts(id=liste.get("id"))[0].get("url"))

dico_listes = {
    liste.get("title"): masto_client.list_accounts(id=liste.get("id"))
    for liste in masto_client.lists()
}
print(
    [account_from_list for liste in dico_listes.values() for account_from_list in liste]
)

try:
    with csv_path_lists.open(
        mode="w", encoding="utf-8", newline=""
    ) as out_csv_lists, csv_path_lists_only_accounts.open(
        mode="w", encoding="utf-8", newline=""
    ) as out_csv_lists_accounts, csv_path_accounts.open(
        mode="w", newline="", encoding="utf-8"
    ) as out_csv_following_accounts:
        # générateurs de CSV
        csv_writer_following_accounts = csv.writer(out_csv_following_accounts)
        csv_writer_listed_accounts_without_lists = csv.writer(out_csv_lists_accounts)
        csv_writer_lists = csv.writer(out_csv_lists)

        # en-tête (colonnes de la première ligne)
        csv_writer_following_accounts.writerow(csv_accounts_columns_names)
        csv_writer_listed_accounts_without_lists.writerow(csv_accounts_columns_names)

        # -- Export des comptes ajoutés à des listes

        # on parcourt les listes du compte authentifié
        for liste in masto_client.lists():
            # Récupérer les membres de chaque liste
            members = masto_client.list_accounts(id=liste.get("id"))

            # on parcourt la liste en la triant sur le nom du compte pour faciliter
            # d'éventuelles comparaisons à l'oeil nu ou autres
            for member in sorted(members, key=lambda x: x["acct"]):
                # Aucune info retournée par l'API ne correspond au formaslime du module
                # import/export de l'application web... ainsi les comptes d'une même
                # instance n'ont pas son adresse. On gère donc cela manuellement
                member_account_full = member.get("acct")
                if "@" not in member_account_full:
                    member_account_full = f"{member_account_full}@mapstodon.space"

                # et zou, dans les CSV
                csv_writer_listed_accounts_without_lists.writerow(
                    (member_account_full, "true", "false", "")
                )
                csv_writer_lists.writerow((liste.get("title"), member_account_full))
        logger.info(
            "L'export des comptes ajoutés à des listes a réussi. "
            f"Comptes (sans les listes) : {csv_path_lists_only_accounts.resolve()}. "
            f"Comptes avec les listes : {csv_path_lists.resolve()}"
        )

        # -- Export de tous les comptes suivis
        for following in masto_client.account_following(id=masto_client.me()):

            member_account_full = following.get("acct")
            if "@" not in member_account_full:
                member_account_full = f"{member_account_full}@mapstodon.space"

            # et zou, dans les CSV
            csv_writer_following_accounts.writerow(
                (member_account_full, "true", "false", "")
            )

        logger.info(
            f"L'export des comptes suivis a réussi: {csv_path_accounts.resolve()}."
        )

except IOError as err:
    logger.critical(
        "Un problème a empêché l'export en CSV des listes et comptes associés. "
        f"Trace : {err}"
    )
