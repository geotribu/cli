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
from datetime import date, datetime
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
            f"Unable to extract year from content location: {input_content_location}"
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


# #############################################################################
# ##### Stand alone program ########
# ##################################

if __name__ == "__main__":
    """Standalone execution."""
    # good
    sample_content_location = (
        "articles/2008/2008-08-22_1-introduction-a-l-api-google-maps/"
    )
    sample_content_date = get_date_from_content_location(sample_content_location)
    print(type(sample_content_date), sample_content_date)
    assert isinstance(sample_content_date, date)

    # good with content folder prefix and md suffix
    sample_content_location = (
        "/content/articles/2008/2008-08-22_1-introduction-a-l-api-google-maps.md"
    )
    sample_content_date = get_date_from_content_location(sample_content_location)
    print(type(sample_content_date), sample_content_date)
    assert isinstance(sample_content_date, date)

    # good with content folder prefix and md suffix
    sample_content_location = "content/rdp/2023/rdp_2023-01-06.md"
    sample_content_date = get_date_from_content_location(sample_content_location)
    print(type(sample_content_date), sample_content_date)
    assert isinstance(sample_content_date, date)

    # bad
    sample_content_location = "2008-08-22_1-introduction-a-l-api-google-maps"
    sample_content_date = get_date_from_content_location(sample_content_location)
    print(type(sample_content_date), sample_content_date)
    assert sample_content_date is None
