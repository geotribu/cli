from typing import Any

import requests
from requests import Response

from geotribu_cli.__about__ import __executable_name__, __version__

HEADERS: dict = {
    b"Accept": b"application/json",
    b"User-Agent": bytes(f"{__executable_name__}/{__version__}", "utf8"),
}


class JsonFeedClient:
    def __init__(self, url: str = "https://geotribu.fr/feed_json_created.json"):
        """Class initialization."""
        self.url = url

    @property
    def get_items(self) -> list[dict[str, Any]]:
        r: Response = requests.get(self.url, headers=HEADERS)
        r.raise_for_status()
        return r.json()["items"]

    def get_tags(self, should_sort: bool = False) -> set[str]:
        tags = set().union(*[i["tags"] for i in self.get_items])
        return sorted(tags) if should_sort else tags
