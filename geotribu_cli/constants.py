#! python3  # noqa: E265


"""Package constants."""


# standard library
import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Literal

# ############################################################################
# ########## GLOBALS #############
# ################################

logger = logging.getLogger(__name__)

# ############################################################################
# ########## CLASSES #############
# ################################


class ExtendedEnum(Enum):
    """Custom Enum with extended methods."""

    @classmethod
    def has_key(cls, name: str) -> bool:
        """Check if a certain key is present in enum.

        Source: https://stackoverflow.com/a/62065380/2556577

        Args:
            name (str): key to check.

        Returns:
            bool: True if the key exists.
        """
        return name in cls.__members__

    @classmethod
    def has_value(cls, value: str) -> bool:
        """Check if a certain value is present in enum.

        Source: https://stackoverflow.com/a/43634746/2556577

        Args:
            value (str): value to check

        Returns:
            bool: True is the value exists.
        """
        return value in cls._value2member_map_

    @classmethod
    def values_set(cls) -> set:
        """Return a set of enum values.

        Returns:
            set of enum's unique values
        """
        return {item.value for item in cls}


class YamlHeaderMandatoryKeys(ExtendedEnum):
    """Clés obligatoires dans l'en-tête d'un contenu Geotribu."""

    AUTHORS = "authors"
    CATEGORIES = "categories"
    DATE = "date"
    DESCRIPTION = "description"
    LICENSE = "license"
    TAGS = "tags"
    TITLE = "title"


class YamlHeaderAvailableLicense(ExtendedEnum):
    """Licences disponibles pour les contenus publiés sur Geotribu."""

    BEERWARE = "beerware"
    CC4_BY_SA = "cc4_by-sa"
    CC4_BY_BC_SA = "cc4_by-nc-sa"
    DEFAULT = "default"


@dataclass
class GeotribuDefaults:
    """Defaults settings for Geotribu."""

    # git
    git_base_url_organisation: str = "https://github.com/geotribu/"

    # website
    site_base_url: str = "https://geotribu.fr/"
    site_git_default_branch: str = "master"
    site_git_project: str = "website"
    site_search_index: str = "search/search_index.json"
    site_search_tags_remote_path = "tags.json"

    # CDN
    cdn_base_url: str = "https://cdn.geotribu.fr/"
    cdn_base_path: str = "img"
    cdn_search_index: str = "search-index.json"

    # comments
    comments_base_url: str = "https://comments.geotribu.fr/"

    # JSON Feed
    json_path_created = "feed_json_created.json"
    json_path_updated = "feed_json_updated.json"

    # RSS
    rss_path_created: str = "feed_rss_created.xml"
    rss_path_updated: str = "feed_rss_updated.xml"

    # images
    images_body_extensions: tuple = (".png", ".jpg", ".jpeg", ".webp")
    images_body_dimensions_max: tuple = (".png", ".jpg", ".jpeg", ".webp")
    images_header_extensions: tuple = (".png", ".jpg", ".jpeg")
    images_header_dimensions_ratio: int = 400 * 800
    images_icon_extensions: tuple = (".png", ".jpg", ".jpeg", ".webp")
    images_icon_dimensions_ratio: int = 400 * 800

    # local working directory
    geotribu_working_folder: Path = Path().home() / ".geotribu"

    # social
    mastodon_base_url: str = "https://mapstodon.space/"

    # templates
    template_article: str = "/articles/templates/template_article.md"
    template_rdp: str = "/rdp/templates/template_rdp.md"
    template_rdp_news: str = "/rdp/templates/template_rdp_news.md"

    @property
    def cdn_search_index_full_url(self) -> str:
        """Returns CDN search index full URL.

        Returns:
            str: URL as string
        """
        return f"{self.cdn_base_url}{self.cdn_base_path}/{self.cdn_search_index}"

    @property
    def json_created_full_url(self) -> str:
        """Returns website JSON Feed full URL for latest created contents.

        Returns:
            str: URL as string
        """
        return f"{self.site_base_url}{self.json_path_created}"

    @property
    def rss_created_full_url(self) -> str:
        """Returns website RSS full URL for latest created contents.

        Returns:
            str: URL as string
        """
        return f"{self.site_base_url}{self.rss_path_created}"

    @property
    def site_search_index_full_url(self) -> str:
        """Returns website search index full URL.

        Returns:
            str: URL as string
        """
        return f"{self.site_base_url}{self.site_search_index}"

    @property
    def site_search_tags_full_url(self) -> str:
        """Returns website search tags full URL.

        Returns:
            str: URL as string
        """
        return f"{self.site_base_url}{self.site_search_tags_remote_path}"

    def site_git_source_base_url(
        self, mode: Literal["blob", "edit", "raw"] = "blob", url_path: str = ""
    ) -> str:
        """Returns website git source URL in three flavors: blob, edit or raw.

        Args:
            mode: display mode for source. Defaults to "blob".

        Returns:
            str: URL as string
        """
        return (
            f"{self.git_base_url_organisation}{self.site_git_project}/{mode}/"
            f"{self.site_git_default_branch}/content"
        )


# -- Stand alone execution
if __name__ == "__main__":
    defaults = GeotribuDefaults()
    print(defaults.cdn_search_index_full_url)
    print(YamlHeaderMandatoryKeys.TITLE.value)
    print("title" in YamlHeaderMandatoryKeys.__members__)
    print("title" in YamlHeaderMandatoryKeys._value2member_map_)
    print({item.value for item in YamlHeaderMandatoryKeys})
