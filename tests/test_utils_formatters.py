#! python3  # noqa E265

"""
    Usage from the repo root folder:

    .. code-block:: bash
        # for whole tests
        python -m unittest tests.test_utils_formatters
        # for specific test
        python -m unittest tests.test_utils_formatters.TestUtilsFormatters.test_convert_octets
"""

# standard library
import unittest

# project
from geotribu_cli.__about__ import __version__
from geotribu_cli.utils.formatters import convert_octets, url_add_utm, url_rm_query

# ############################################################################
# ########## Classes #############
# ################################


class TestUtilsFormatters(unittest.TestCase):
    """Test package utilities."""

    def test_convert_octets(self):
        """Test file size formatter."""
        self.assertEqual(
            convert_octets(1024),
            "1.0 Ko",
        )

        self.assertEqual(
            convert_octets(2097152),
            "2.0 Mo",
        )

    def test_url_rm_query_parameters(self):
        """Test URL query params manipulations."""
        self.assertEqual(
            url_rm_query(
                in_url="https://geotribu.fr/rdp/2023/rdp_2023-05-12/?utm_campaign=feed-syndication&utm_medium=RSS&utm_source=rss-feed",
                param_startswith="utm_",
            ),
            "https://geotribu.fr/rdp/2023/rdp_2023-05-12/",
        )
        self.assertEqual(
            url_add_utm(
                in_url="https://geotribu.fr/rdp/2023/rdp_2023-05-12/?utm_campaign=feed-syndication&utm_medium=RSS&utm_source=rss-feed",
            ),
            f"https://geotribu.fr/rdp/2023/rdp_2023-05-12/?utm_source=geotribu_cli&utm_medium=GeotribuToolbelt&utm_campaign=geotribu_cli_{__version__}",
        )


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
