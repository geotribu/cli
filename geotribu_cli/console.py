#! python3  # noqa: E265

"""
Shared console instance.

See: https://rich.readthedocs.io/en/stable/console.html
"""

# ############################################################################
# ########## IMPORTS #############
# ################################

# 3rd party
from rich.console import Console

# ############################################################################
# ########## GLOBALS #############
# ################################

console = Console(record=True, stderr=True)
