#! python3  # noqa: E265

# standard library
from math import floor
from math import log as math_log

# ############################################################################
# ########## FUNCTIONS ###########
# ################################


def convert_octets(octets: int) -> str:
    """Convert a mount of octets in readable size.

    Args:
        octets (int): mount of octets to convert

    Returns:
        str: _description_

    Example:
    .. code-block:: python
        >>> convert_octets(1024)
        "1ko"
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
