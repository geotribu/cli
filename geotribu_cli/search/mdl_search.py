#! python3  # noqa: E265


"""Search related models."""


# standard library
from typing import TypedDict

# ############################################################################
# ########## CLASSES #############
# ################################


class MkdocsSearchConfiguration(TypedDict, total=False):
    """Search configuration in Mkdocs (lunr.py under the hood)."""

    # approximate, since config structure may vary
    lang: list[str]
    separator: str
    pipeline: list[str]
    fields: dict[str, dict[str, float]]


class MkdocsSearchDocument(TypedDict):
    """Search document structure in Mkdocs (lunr.py under the hood)."""

    location: str
    tags: list[str]
    text: str
    title: str


class MkdocsSearchListing(TypedDict):
    """Mkdocs listing search (lunr.py under the hood)."""

    config: MkdocsSearchConfiguration
    docs: list[MkdocsSearchDocument]
