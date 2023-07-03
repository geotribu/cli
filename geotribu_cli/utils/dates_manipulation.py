#! python3  # noqa: E265

"""
    Extract date from content path, location or name.

    Author: Julien Moura (https://github.com/guts)
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
from calendar import monthrange
from datetime import date, datetime, timedelta
from functools import lru_cache

# #############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)

# #############################################################################
# ########## Functions #############
# ##################################


@lru_cache(maxsize=512)
def is_more_recent(date_ref: date, date_to_compare: date) -> bool:
    """Détermine si la date à comparer est plus récent que la date de référence.

    Args:
        date_ref: date de référence
        date_to_compare: date à comparer

    Returns:
        résultat de la comparaison
    """
    return date_to_compare > date_ref


@lru_cache(maxsize=512)
def get_date_from_content_location(input_content_location: str) -> date:
    """Extract date from content location string.

    Args:
        input_content_location (str): content location path.

    Returns:
        date: date object

    Example:

    .. code-block:: python

        > sample_content_location = (
            "articles/2008/2008-08-22_1-introduction-a-l-api-google-maps/"
        )
        > sample_content_date = get_date_from_content_location(sample_content_location)
        > print(type(sample_content_date), sample_content_date)
        <class 'datetime.date'> 2008-08-22

    """
    # checks
    if not isinstance(input_content_location, str) or "/" not in input_content_location:
        logger.error(
            ValueError(f"Input location seems to be invalid: {input_content_location}.")
        )
        return None

    try:
        # get the year
        parts = input_content_location.split("/")
        year = [p for p in parts if p.isdigit()][0]
    except Exception as err:
        logger.error(
            f"Unable to extract year from content location: {input_content_location}. "
            f"Trace: {err}."
        )
        return None

    # get next part
    next_part = parts[parts.index(year) + 1]

    # clean next part for rdp
    if next_part.startswith("rdp_"):
        next_part = next_part[4:]

    # now, the next part should contain the date within the first 10 chars
    date_str = next_part[:10]

    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except Exception as err:
        logger.error(err)
        return None


def get_days_until_next_month(from_date: date = None) -> int:
    """Return the number of days until the next month.

    Args:
        from_date: date to compare to next month. If not set, datetime.date.today()
            is used.

    Returns:
        number of days until next month
    """
    if from_date is None:
        logger.debug("Aucune date passée. Date du jour utilisée.")
        from_date = date.today()

    next_month = date(from_date.year, from_date.month, 1) + timedelta(
        days=monthrange(year=from_date.year, month=from_date.month)[1]
    )
    diff = next_month - from_date

    return diff.days


# #############################################################################
# ##### Stand alone program ########
# ##################################

if __name__ == "__main__":
    """Standalone execution."""
    pass
