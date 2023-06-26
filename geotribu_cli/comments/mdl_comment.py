#! python3  # noqa: E265


"""Package constants."""


# standard library
import logging
from dataclasses import dataclass
from datetime import datetime
from html import unescape

# 3rd party
from markdownify import markdownify

# package
from geotribu_cli.constants import GeotribuDefaults

# ############################################################################
# ########## GLOBALS #############
# ################################

logger = logging.getLogger(__name__)

# ############################################################################
# ########## CLASSES #############
# ################################


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
