import csv
from os import getenv

import requests

from geotribu_cli.__about__ import __title_clean__, __version__
from geotribu_cli.constants import GeotribuDefaults

defaults_settings = GeotribuDefaults()


# prepare requests session object
headers = {
    "User-Agent": f"{__title_clean__}-dev/{__version__}",
    "Content-Type": "application/json; charset=utf-8",
    "Authorization": f"Bearer {getenv('GEOTRIBU_MASTODON_API_ACCESS_TOKEN')}",
}

req_session = requests.Session()
req_session.headers = headers


# get lists
geotribu_lists = req_session.get(
    url=f"{defaults_settings.mastodon_base_url}api/v1/lists",
)

# print(f"listes : {geotribu_lists.json()}")


for liste in geotribu_lists.json():
    liste_accounts = req_session.get(
        url=f"{defaults_settings.mastodon_base_url}api/v1/lists/{liste.get('id')}/accounts"
    )
    print(f"\n'{liste.get('title')}: {liste_accounts.json()}")

req_session.close()
