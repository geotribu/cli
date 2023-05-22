#! python3  # noqa: E265

"""Helpers to format text and variables."""


# standard library
import logging
from functools import lru_cache
from math import floor
from math import log as math_log
from typing import Literal
from urllib.parse import parse_qs, urlsplit, urlunsplit

# package
from geotribu_cli.__about__ import __title_clean__, __version__
from geotribu_cli.constants import GeotribuDefaults

# ############################################################################
# ########## GLOBALS #############
# ################################

logger = logging.getLogger(__name__)
defaults_settings = GeotribuDefaults()

# ############################################################################
# ########## FUNCTIONS ###########
# ################################


def convert_octets(octets: int) -> str:
    """Convert a mount of octets in readable size.

    Args:
        octets (int): mount of octets to convert

    Returns:
        str: size in a human readable format: ko, Mo, etc.

    Example:

    .. code-block:: python

        >>> convert_octets(1024)
        "1 ko"
        >>> from pathlib import Path
        >>> convert_octets(Path(my_file.txt).stat().st_size)
    """
    # check zero
    if octets == 0:
        return "0 octet"

    # conversion
    size_name = ("octets", "Ko", "Mo", "Go", "To", "Po")
    i = int(floor(math_log(octets, 1024)))
    p = pow(1024, i)
    s = round(octets / p, 2)

    return f"{s} {size_name[i]}"


@lru_cache(maxsize=256, typed=True)
def url_rm_query(in_url: str, param_startswith: str = "utm_") -> str:
    """Remove existing utm_* query parameters from input URL.

    Returns:
        str: URL without utm_* query parameters
    """
    parsed_url = urlsplit(url=in_url)
    url_query_in = parse_qs(parsed_url.query)
    url_query_out = {}
    for param, value in url_query_in.items():
        if param.startswith(param_startswith):
            continue
        url_query_out[param] = value

    return urlunsplit(parsed_url._replace(query=url_query_out))


@lru_cache(maxsize=256, typed=True)
def url_add_utm(in_url: str) -> str:
    """Adds utm_* query parameters to the item URL.

    Returns:
        str: URLs with utm_* query parameters to track openings from this package.
    """
    parsed_url = urlsplit(url=url_rm_query(in_url))

    return urlunsplit(
        parsed_url._replace(
            query=f"utm_source=geotribu_cli"
            f"&utm_medium={__title_clean__}"
            f"&utm_campaign=geotribu_cli_{__version__}"
        )
    )


@lru_cache(maxsize=256)
def url_content_source(
    in_url: str,
    mode: Literal["blob", "edit", "raw"] = "blob",
) -> str:
    """Adds utm_* query parameters to the item URL.

    Args:
        mode (Literal[&quot;blob&quot;, &quot;edit&quot;, &quot;raw&quot;], optional): display mode for source. Defaults to "blob".
        url_path (str, optional): content path. Defaults to "".

    Returns:
        str: URLs with utm_* query parameters to track openings from this package.
    """
    parsed_url = urlsplit(url=url_rm_query(in_url))

    # clean trailing slash from path
    if parsed_url.path.endswith("/"):
        url_path = parsed_url.path[:-1]
    else:
        url_path = parsed_url.path

    if in_url.startswith(defaults_settings.site_base_url):
        return f"{defaults_settings.site_git_source_base_url(mode=mode)}{url_path}.md"
