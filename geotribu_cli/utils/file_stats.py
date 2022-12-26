#! python3  # noqa: E265

"""Check file statistcs."""

# ############################################################################
# ########## IMPORTS #############
# ################################

# standard library
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Literal

# ############################################################################
# ########## GLOBALS #############
# ################################

# logs
logger = logging.getLogger(__name__)

# ############################################################################
# ########## FUNCTIONS ###########
# ################################


def is_file_older_than(
    local_file_path: Path,
    expiration_rotating_hours: int = 24,
    dt_reference_mode: Literal["c", "m"] = "c",
) -> bool:
    """Check if the creation/modification date of the specified file is older than the \
        mount of hours.

    Args:
        local_file_path (Path): local path to the index file
        expiration_rotating_hours (int, optional): number in hours to consider the \
            local file outdated. Defaults to 24.
        dt_reference_mode (Literal['c', 'm'], optional): reference date type: c for \
            creation date, m for modification. Defaults to "c".
    Returns:
        bool: True if the creation/modification date of the file is older than the \
            specified number of hours.
    """
    # get file reference datetime - modification or creation
    if dt_reference_mode == "m":
        f_ref_dt = datetime.fromtimestamp(local_file_path.stat().st_mtime)
        dt_type = "modified"
    else:
        f_ref_dt = datetime.fromtimestamp(local_file_path.stat().st_ctime)
        dt_type = "created"

    if (datetime.now() - f_ref_dt) < timedelta(hours=expiration_rotating_hours):
        logger.debug(
            f"{local_file_path} has been {dt_type} less than "
            f"{expiration_rotating_hours} hours ago."
        )
        return False
    else:
        logger.debug(
            f"{local_file_path} has been {dt_type} more than "
            f"{expiration_rotating_hours} hours ago."
        )
        return True
