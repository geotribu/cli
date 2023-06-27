#! python3  # noqa: E265


"""Search related models."""


# standard library
from dataclasses import dataclass

# ############################################################################
# ########## CLASSES #############
# ################################


@dataclass
class MkdocsSearchConfiguration:
    """Search configuration in Mkdocs."""

    lang: list
    separator: str


@dataclass
class MkdocsSearchDocument:
    """Search document structure in Mkdocs."""

    location: str
    tags: list
    text: str
    title: str


@dataclass
class MkdocsSearchListing:
    """Mkdocs listing search."""

    config: MkdocsSearchConfiguration
    docs: list[MkdocsSearchDocument]
