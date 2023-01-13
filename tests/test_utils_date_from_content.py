#! python3  # noqa E265

"""
    Usage from the repo root folder:

    .. code-block:: bash
        # for whole tests
        python -m unittest tests.test_utils_date_from_content
        # for specific test
        python -m unittest tests.test_utils_date_from_content.TestUtilsDateFromContent.test_date_from_content_location
"""

# standard library
import unittest
from datetime import date

# project
from geotribu_cli.utils.date_from_content import get_date_from_content_location

# ############################################################################
# ########## Classes #############
# ################################


class TestUtilsDateFromContent(unittest.TestCase):
    """Test package utilities."""

    def test_date_from_content_location(self):
        """Test minimalist slugify function."""
        # good
        sample_content_location = (
            "articles/2008/2008-08-22_1-introduction-a-l-api-google-maps/"
        )
        sample_content_date = get_date_from_content_location(sample_content_location)
        print(type(sample_content_date), sample_content_date)
        self.assertIsInstance(sample_content_date, date)

        # good with content folder prefix and md suffix
        sample_content_location = (
            "/content/articles/2008/2008-08-22_1-introduction-a-l-api-google-maps.md"
        )
        sample_content_date = get_date_from_content_location(sample_content_location)
        print(type(sample_content_date), sample_content_date)
        self.assertIsInstance(sample_content_date, date)

        # good with content folder and rdp_ prefixes
        sample_content_location = "content/rdp/2023/rdp_2023-01-06"
        sample_content_date = get_date_from_content_location(sample_content_location)
        print(type(sample_content_date), sample_content_date)
        assert isinstance(sample_content_date, date)

        # bad
        sample_content_location = "2008-08-22_1-introduction-a-l-api-google-maps"
        sample_content_date = get_date_from_content_location(sample_content_location)
        print(type(sample_content_date), sample_content_date)
        self.assertIsNone(sample_content_date)


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
