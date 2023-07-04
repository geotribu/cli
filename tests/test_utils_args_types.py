#! python3  # noqa E265

"""
    Usage from the repo root folder:

    .. code-block:: bash
        # for whole tests
        python -m unittest tests.test_utils_args_types
        # for specific test
        python -m unittest tests.test_utils_args_types.TestUtilsArgsTypes.test_arg_type_folder_path
"""


# standard library
import unittest
from argparse import ArgumentTypeError
from datetime import date, timedelta
from pathlib import Path

# project
from geotribu_cli.utils.args_types import (
    arg_date_iso,
    arg_date_iso_max_today,
    arg_type_path_folder,
)

# ############################################################################
# ########## Classes #############
# ################################


class TestUtilsArgsTypes(unittest.TestCase):
    """Test argparse custom types."""

    def test_arg_type_folder_path(self):
        """Test folder path check."""
        self.assertIsInstance(arg_type_path_folder("./tests"), Path)
        with self.assertRaises(ArgumentTypeError):
            arg_type_path_folder(2121)

    def test_arg_type_date_iso(self):
        """Test folder path check."""
        self.assertIsInstance(arg_date_iso("2023-09-08"), date)
        with self.assertRaises(ArgumentTypeError):
            arg_date_iso("2023-09-08 15:20")

    def test_arg_type_date_iso_max_today(self):
        """Test folder path check."""
        self.assertIsInstance(arg_date_iso_max_today("2023-09-08"), date)

        tomorrow = date.today() + timedelta(days=1)
        self.assertEqual(arg_date_iso_max_today(f"{tomorrow:%Y-%m-%d}"), date.today())
        with self.assertRaises(ArgumentTypeError):
            arg_date_iso_max_today("2023-09-08 15:20")
