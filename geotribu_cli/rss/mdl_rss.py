#! python3  # noqa: E265


"""Package constants."""


# standard library
from dataclasses import dataclass


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
