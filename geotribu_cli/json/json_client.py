#! python3  # noqa: E265


"""JSON Feed client."""


# ############################################################################
# ########## IMPORTS #############
# ################################

# standard
import logging
from pathlib import Path
from typing import Any

# 3rd party
import orjson

# project
from geotribu_cli.constants import GeotribuDefaults
from geotribu_cli.utils.file_downloader import download_remote_file_to_local

# ############################################################################
# ########## GLOBALS #############
# ################################

logger = logging.getLogger(__name__)
defaults_settings = GeotribuDefaults()


# ############################################################################
# ########## CLASSES #############
# ################################


class JsonFeedClient:
    """JSON Feed client."""

    def __init__(
        self,
        json_feed_url: str = defaults_settings.json_created_full_url,
        tags_url: str = defaults_settings.site_search_tags_full_url,
        expiration_rotating_hours: int = 24,
    ):
        """Class initialization.

        Args:
            url: JSON feed URL, defaults to https://geotribu.fr/feed_json_created.json
            tags_url: JSON tags URL, defaults to https://geotribu.fr/tags.json
            expiration_rotating_hours: nombre d'heures à partir duquel considérer
                le fichier local comme périmé. Defaults to 24.
        """
        # params as attributes
        self.json_feed_url = json_feed_url
        self.tags_url = tags_url
        self.expiration_rotating_hours = expiration_rotating_hours

        # attributes
        self.local_json_feed_path: Path = (
            defaults_settings.geotribu_working_folder.joinpath("rss/json_feed.json")
        )
        self.local_json_feed_path.parent.mkdir(parents=True, exist_ok=True)
        self.local_tags_path: Path = defaults_settings.geotribu_working_folder.joinpath(
            "search/tags.json"
        )
        self.local_tags_path.parent.mkdir(parents=True, exist_ok=True)

    def items(self) -> list[dict[str, Any]]:
        """Fetch Geotribu JSON feed latest created items.

        Returns:
            List of dicts representing raw JSON feed items
        """

        local_json_feed = download_remote_file_to_local(
            remote_url_to_download=self.json_feed_url,
            local_file_path=self.local_json_feed_path,
            expiration_rotating_hours=self.expiration_rotating_hours,
        )

        with local_json_feed.open("rb") as fd:
            json_feed = orjson.loads(fd.read())

        return json_feed.get("items")

    def tags(self, should_sort: bool = False) -> list[str]:
        """Fetch Geotribu used tags.

        Args:
            should_sort: if the list of returned tags should be alphabetically sorted.
                Defaults to False.

        Returns:
            List of tags used by Geotribu
        """
        local_tags = download_remote_file_to_local(
            remote_url_to_download=self.tags_url,
            local_file_path=self.local_tags_path,
            expiration_rotating_hours=self.expiration_rotating_hours,
        )

        with local_tags.open("rb") as fd:
            search_tags = orjson.loads(fd.read())

        tags = set()
        for item in search_tags.get("mappings"):
            for tag in item["tags"]:
                tags.add(tag)
        return sorted(tags) if should_sort else list(tags)
