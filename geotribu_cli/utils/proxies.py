#! python3  # noqa: E265

"""Micro helper to retrieve network proxy settings from system.

Author: Julien Moura (github.com/guts)
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
from os import environ
from typing import Union
from urllib.request import getproxies

# #############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)


# #############################################################################
# ########## Functions #############
# ##################################


def get_proxy_settings() -> Union[dict, None]:
    """Retrieves network proxy settings from operating system configuration or \
    environment variables.

    Returns:
        Union[dict, None]: system proxy settings or None if no proxy is set
    """
    if environ.get("HTTP_PROXY") or environ.get("HTTPS_PROXY"):
        proxy_settings = {
            "http": environ.get("HTTP_PROXY"),
            "https": environ.get("HTTPS_PROXY"),
        }
        logger.debug(
            "Proxies settings found in environment vars (loaded from .env file): {}".format(
                proxy_settings
            )
        )
    elif getproxies():
        proxy_settings = getproxies()
        logger.debug(f"Proxies settings found in the OS: {proxy_settings}")
    else:
        logger.debug("No proxy settings found in environment vars nor OS settings.")
        proxy_settings = None

    return proxy_settings


# #############################################################################
# ##### Stand alone program ########
# ##################################

if __name__ == "__main__":
    """Standalone execution."""
    pass
