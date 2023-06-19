#! python3  # noqa: E265


"""Package constants."""


# standard library
import logging
from dataclasses import dataclass
from datetime import datetime
from html import unescape
from pathlib import Path
from typing import Literal

# 3rd party
from markdownify import markdownify

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
            mode (Literal[&quot;blob&quot;, &quot;edit&quot;, &quot;raw&quot;], optional): display mode for source. Defaults to "blob".

        Returns:
            str: URL as string
        """
        return (
            f"{self.git_base_url_organisation}{self.site_git_project}/{mode}/"
            f"{self.site_git_default_branch}/content"
        )


@dataclass
class Comment:
    """Structure of an Isso comment."""

    # mandatory
    author: str
    created: float
    dislikes: int
    id: str
    likes: int
    mode: int
    text: str
    uri: str
    # default args
    modified: float = None
    parent: int = None
    website: str = None

    @property
    def created_as_datetime(self) -> datetime:
        """Created date as datetime object.

        Returns:
            datetime object
        """
        if self.created is not None:
            return datetime.fromtimestamp(self.created)

    @property
    def modified_as_datetime(self) -> datetime:
        """Modified date as datetime object.

        Returns:
            datetime object
        """
        if self.modified is not None:
            return datetime.fromtimestamp(self.modified)

    @property
    def markdownified_text(self) -> str:
        """Return text converted into Markdown. If conversion fails, it returns
            unescaped text.

        Returns:
            comment text in Markdown
        """
        try:
            return markdownify(self.text)
        except Exception as err:
            logger.error(err)
            return self.unescaped_text

    @property
    def unescaped_text(self) -> str:
        """Return text with unescaped HTML tags.

        Returns:
            text with converted escape chars
        """
        try:
            return unescape(self.text)
        except Exception as err:
            logger.error(err)
            return self.text

    @property
    def url_to_comment(self) -> str:
        """Full URL to the comment online.

        Returns:
            URL
        """
        defaults_settings = GeotribuDefaults()

        # handle double slash in URL
        base_url = defaults_settings.site_base_url
        if base_url.endswith("/") and self.uri.startswith("/"):
            base_url = base_url[:-1]

        return f"{base_url}{self.uri}#isso-{self.id}"


# Data structures
@dataclass
class RssItem:
    """Model for an RSS item."""

    abstract: str = None
    author: str = None
    categories: list = None
    date_pub: str = None
    guid: str = None
    image_length: str = None
    image_type: str = None
    image_url: str = None
    title: str = None
    url: str = None


@dataclass
class MkdocsSearchConfiguration:
    """Search configuration in Mkdocs."""

    lang: list
    separator: str


@dataclass
class MkdocsSearchDocument:
    """Search document structure in Mkdocs."""

    title: str
    text: str
    location: str
    tags: list


@dataclass
class MkdocsSearchListing:
    """Mkdocs listing search."""

    config: MkdocsSearchConfiguration
    docs: list[MkdocsSearchDocument]


# -- Stand alone execution
if __name__ == "__main__":
    defaults = GeotribuDefaults()
    print(defaults.cdn_search_index_full_url)
