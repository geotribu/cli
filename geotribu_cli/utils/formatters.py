#! python3  # noqa: E265

"""Helpers to format text and variables."""


# standard library
from functools import lru_cache
from math import floor
from math import log as math_log
from urllib.parse import parse_qs, urlsplit, urlunsplit

# package
from geotribu_cli.__about__ import __title_clean__, __version__

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
