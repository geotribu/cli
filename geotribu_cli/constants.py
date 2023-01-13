#! python3  # noqa: E265


"""Package constants."""

# standard library
from dataclasses import dataclass


@dataclass
class GeotribuDefaults:
    """Defaults settings for Geotribu."""

    # git
    git_base_url_organisation: str = "https://github.com/geotribu/"
    # website
    site_base_url: str = "https://static.geotribu.fr/"
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
    lang: list
    separator: str


@dataclass
class MkdocsSearchDocument:
    title: str
    text: str
    location: str
    tags: list


@dataclass
class MkdocsSearchListing:
    config: MkdocsSearchConfiguration
    docs: list[MkdocsSearchDocument]


# -- Stand alone execution
if __name__ == "__main__":
    defaults = GeotribuDefaults()
    print(defaults.cdn_search_index_full_url)
