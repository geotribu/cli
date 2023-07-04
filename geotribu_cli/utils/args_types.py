#! python3  # noqa: E265

"""Static objects and variables."""

# ############################################################################
# ########## IMPORTS #############
# ################################


# standard lib
import logging
from argparse import ArgumentTypeError
from datetime import date
from pathlib import Path
from typing import Union

# package
from geotribu_cli.utils.check_path import check_path
from geotribu_cli.utils.dates_manipulation import is_more_recent

# ############################################################################
# ########## GLOBALS #############
# ################################

logger = logging.getLogger(__name__)


# ############################################################################
# ########## FUNCTIONS ###########
# ################################
def arg_date_iso(date_str: str) -> date:
    """
    Valide le format d'une date au format AAAA-MM-JJ.

    Args:
        date_str (str): Date au format AAAA-MM-JJ.

    Returns:
        datetime: Objet datetime représentant la date.

    Raises:
        ArgumentTypeError: Erreur en cas de format de date incorrect.
    """
    try:
        return date.fromisoformat(date_str)
    except ValueError:
        raise ArgumentTypeError(
            f"Le format de date doit être AAAA-MM-JJ. Valeur passée : {date_str}"
        )


def arg_date_iso_max_today(date_str: str) -> date:
    """Valide le format d'une date au format AAAA-MM-JJ et vérifie que la date n'est pas
        ultérieure à la date du jour. Sinon, retourne la date du jour.

    Args:
        date_str (str): Date au format AAAA-MM-JJ.

    Returns:
        datetime: Objet datetime représentant la date.

    Raises:
        ArgumentTypeError: Erreur en cas de format de date incorrect.
    """
    date_obj = arg_date_iso(date_str)

    if is_more_recent(
        date_ref=date.today(),
        date_to_compare=date_obj,
    ):
        logger.info(
            f"La date {date_obj} est ultérieure à la date du jour. "
            f"C'est donc celle-ci qui sera utilisée : {date.today()}."
        )
        date_obj = date.today()

    return date_obj


def arg_type_path_folder(input_path: Union[Path, str]) -> Path:
    """Check an argparse argument type, expecting a valid folder path.

    Args:
        input_path (Union[Path, str]): path to check as string or pathlib.Path

    Raises:
        ArgumentTypeError: if the input path is not a valid type or not a folder or
        doesn't exist.

    Returns:
        Path: path to the folder as pathlib.Path
    """
    if not check_path(
        input_path=input_path,
        must_exists=True,
        must_be_a_folder=True,
        must_be_readable=True,
        must_be_writable=True,
        raise_error=False,
    ):
        raise ArgumentTypeError(
            f"{input_path} is not a valid folder path. Check the logs."
        )

    return Path(input_path)
