from typing import Any

import requests
from requests import Response

from geotribu_cli.__about__ import __executable_name__, __version__

JSON_FEED_URL = "https://geotribu.fr/feed_json_created.json"
JSON_TAGS_URL = "https://geotribu.fr/tags.json"

HEADERS: dict = {
    b"Accept": b"application/json",
    b"User-Agent": bytes(f"{__executable_name__}/{__version__}", "utf8"),
}


class JsonFeedClient:
    def __init__(self, url: str = JSON_FEED_URL, tags_url: str = JSON_TAGS_URL):
        """
        Class initialization

        Args:
            url: JSON feed URL, defaults to https://geotribu.fr/feed_json_created.json
            tags_url: JSON tags URL, defaults to https://geotribu.fr/tags.json
        """
        self.url = url
        self.tags_url = tags_url

    def items(self) -> list[dict[str, Any]]:
        """
        Fetch Geotribu JSON feed items

        Returns:
            List of dicts representing raw JSON feed items
        """
        r: Response = requests.get(self.url, headers=HEADERS)
        r.raise_for_status()
        return r.json()["items"]

    def tags(self, should_sort: bool = False) -> list[str]:
        """
        Fetch Geotribu used tags

        Args:
            should_sort: if the list of returned tags should be alphabetically sorted

        Returns:
            List of tags used by Geotribu
        """
        r: Response = requests.get(self.tags_url, headers=HEADERS)
        r.raise_for_status()
        tags = set()
        for item in r.json()["mappings"]:
            for tag in item["tags"]:
                tags.add(tag)
        return sorted(tags) if should_sort else list(tags)
