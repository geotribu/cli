#! python3  # noqa: E265


"""Package constants."""


# standard library
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

# ############################################################################
# ########## GLOBALS #############
# ################################

logger = logging.getLogger(__name__)

# ############################################################################
# ########## CLASSES #############
# ################################


@dataclass
class GeotribuDefaults:
    """Defaults settings for Geotribu."""

    # git
    git_base_url_organisation: str = "https://github.com/geotribu/"

    # website
    site_base_url: str = "https://static.geotribu.fr/"
    site_git_default_branch: str = "master"
    site_git_project: str = "website"
    site_search_index: str = "search/search_index.json"

    # CDN
    cdn_base_url: str = "https://cdn.geotribu.fr/"
    cdn_base_path: str = "img"
    cdn_search_index: str = "search-index.json"

    # comments
    comments_base_url: str = "https://comments.geotribu.fr/"

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
