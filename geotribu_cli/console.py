#! python3  # noqa: E265

"""
Shared console instance.

See: https://rich.readthedocs.io/en/stable/console.html
"""

# ############################################################################
# ########## IMPORTS #############
# ################################

# standard
import locale
import logging
from sys import platform as opersys

# 3rd party
from rich.console import Console

# ############################################################################
# ########## GLOBALS #############
# ################################
logger = logging.getLogger(__name__)

try:
    if opersys == "win32":
        locale.setlocale(locale.LC_TIME, "fra_fra")
        logger.debug("Locale des variables de temps définie sur fra_fra")
    else:
        locale.setlocale(locale.LC_TIME, "fr_FR.utf8")
        logger.debug("Locale des variables de temps définie sur fr_FR.utf8")
except Exception as error:
    logger.warning(f"Unable to set the French locale. Trace: {error}")


console = Console(record=True, stderr=False)
