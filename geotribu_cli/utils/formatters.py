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
        octets: mount of octets to convert

    Returns:
        size in a human readable format: ko, Mo, etc.

    Example:

    .. code-block:: python

        >>> convert_octets(1024)
        1 ko
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
def url_add_utm(in_url: str) -> str:
    """Adds utm_* query parameters to the item URL.

    Args:
        in_url: input content URL.

    Returns:
        URL with utm_* query parameters to track openings from this package.

    Example:

    .. code-block:: python

        >>> print(url_add_utm("https://geotribu.fr/articles/test/"))
        https://geotribu.fr/articles/test/?utm_source=geotribu_cli&utm_medium=GeotribuToolbelt&utm_campaign=geotribu_cli_0.16.0
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
def url_content_name(
    in_url: str,
) -> str:
    """Retrieve filename from a content URL.

    Args:
        in_url: input content URL.

    Returns:
        filename at the end of URL.

    Example:

    .. code-block:: python

        >>> print(url_content_source("https://static.geotribu.fr/articles/2023/2023-05-04_annonce-changement-url-site-geotribu/"))
        https://github.com/geotribu/website/blob/master/content/articles/2023/2023-05-04_annonce-changement-url-site-geotribu.md
        >>> print(url_content_source("https://static.geotribu.fr/articles/2023/2023-05-04_annonce-changement-url-site-geotribu/", mode='raw'))
        https://github.com/geotribu/website/raw/master/content/articles/2023/2023-05-04_annonce-changement-url-site-geotribu.md
        >>> print(url_content_source("https://static.geotribu.fr/articles/2023/2023-05-04_annonce-changement-url-site-geotribu/", mode='edit'))
        https://github.com/geotribu/website/edit/master/content/articles/2023/2023-05-04_annonce-changement-url-site-geotribu.md
    """
    parsed_url = urlsplit(url=url_rm_query(in_url))

    # clean trailing slash from path
    if parsed_url.path.endswith("/"):
        url_path = parsed_url.path[:-1]
    else:
        url_path = parsed_url.path

    return url_rm_query(url_path).split("/")[-1]


@lru_cache(maxsize=256)
def url_content_source(
    in_url: str,
    mode: Literal["blob", "edit", "raw"] = "blob",
) -> str:
    """Retrieve remote source file from a content URL.

    Args:
        mode: display mode for source. Defaults to "blob".
        in_url: input content URL. Defaults to "".

    Returns:
        URLs with utm_* query parameters to track openings from this package.

    Example:

    .. code-block:: python

        >>> print(url_content_source("https://static.geotribu.fr/articles/2023/2023-05-04_annonce-changement-url-site-geotribu/"))
        https://github.com/geotribu/website/blob/master/content/articles/2023/2023-05-04_annonce-changement-url-site-geotribu.md
        >>> print(url_content_source("https://static.geotribu.fr/articles/2023/2023-05-04_annonce-changement-url-site-geotribu/", mode='raw'))
        https://github.com/geotribu/website/raw/master/content/articles/2023/2023-05-04_annonce-changement-url-site-geotribu.md
        >>> print(url_content_source("https://static.geotribu.fr/articles/2023/2023-05-04_annonce-changement-url-site-geotribu/", mode='edit'))
        https://github.com/geotribu/website/edit/master/content/articles/2023/2023-05-04_annonce-changement-url-site-geotribu.md
    """
    parsed_url = urlsplit(url=url_rm_query(in_url))

    # clean trailing slash from path
    if parsed_url.path.endswith("/"):
        url_path = parsed_url.path[:-1]
    else:
        url_path = parsed_url.path

    if in_url.startswith(defaults_settings.site_base_url):
        return f"{defaults_settings.site_git_source_base_url(mode=mode)}{url_path}.md"


@lru_cache(maxsize=256, typed=True)
def url_rm_query(in_url: str, param_startswith: str = "utm_") -> str:
    """Remove existing query parameters (default: utm_*) from input URL.

    Args:
        in_url: input URL to clean
        param_startswith: start pattern of param to remove. Defaults to 'utm_'.

    Returns:
        URL without query parameters

    Example:

    .. code-block:: python

        >>> print(url_rm_query("https://geotribu.fr/articles/test/?utm_source=geotribu_cli&utm_medium=GeotribuToolbelt&utm_campaign=geotribu_cli_0.16.0"))
        https://geotribu.fr/articles/test/
    """
    parsed_url = urlsplit(url=in_url)
    url_query_in = parse_qs(parsed_url.query)
    url_query_out = {}
    for param, value in url_query_in.items():
        if param.startswith(param_startswith):
            continue
        url_query_out[param] = value

    return urlunsplit(parsed_url._replace(query=url_query_out))
