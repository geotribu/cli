#! python3


"""Search related models."""

# standard library
from typing import Literal, NotRequired, TypedDict

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
    indexing: str
    min_search_length: int
    prebuild_index: Literal["python"] | bool


class MkdocsSearchDocument(TypedDict):
    """Search document structure in Mkdocs (lunr.py under the hood)."""

    location: str
    tags: NotRequired[list[str]]
    text: str
    title: str


class MkdocsSearchListing(TypedDict):
    """Mkdocs listing search (lunr.py under the hood)."""

    config: MkdocsSearchConfiguration
    docs: list[MkdocsSearchDocument]
    index: NotRequired[dict]
