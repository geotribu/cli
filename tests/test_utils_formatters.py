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
from geotribu_cli.utils.formatters import (
    convert_octets,
    url_add_utm,
    url_content_name,
    url_content_source,
    url_rm_query,
)

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

    def test_url_add_query_utm_parameters(self):
        """Test URL query params add."""
        self.assertEqual(
            url_add_utm(
                in_url="https://geotribu.fr/rdp/2023/rdp_2023-05-12/?utm_campaign=feed-syndication&utm_medium=RSS&utm_source=rss-feed",
            ),
            f"https://geotribu.fr/rdp/2023/rdp_2023-05-12/?utm_source=geotribu_cli&utm_medium=GeotribuToolbelt&utm_campaign=geotribu_cli_{__version__}",
        )

    def test_url_content_name(self):
        """Test URL content name extraction."""
        self.assertEqual(
            url_content_name(
                "https://static.geotribu.fr/articles/2023/2023-05-04_annonce-changement-url-site-geotribu/"
            ),
            "2023-05-04_annonce-changement-url-site-geotribu",
        )

        self.assertEqual(
            url_content_name(
                "https://cdn.geotribu.fr/img/logos-icones/logiciels_librairies/FME.png"
            ),
            "FME.png",
        )

    def test_url_content_source(self):
        """Test URL query params add."""
        self.assertEqual(
            url_content_source(
                "https://static.geotribu.fr/articles/2023/2023-05-04_annonce-changement-url-site-geotribu/"
            ),
            "https://github.com/geotribu/website/blob/master/content/articles/2023/2023-05-04_annonce-changement-url-site-geotribu.md",
        )
        self.assertEqual(
            url_content_source(
                "https://static.geotribu.fr/articles/2023/2023-05-04_annonce-changement-url-site-geotribu/",
                mode="raw",
            ),
            "https://github.com/geotribu/website/raw/master/content/articles/2023/2023-05-04_annonce-changement-url-site-geotribu.md",
        )
        self.assertEqual(
            url_content_source(
                "https://static.geotribu.fr/articles/2023/2023-05-04_annonce-changement-url-site-geotribu/",
                mode="edit",
            ),
            "https://github.com/geotribu/website/edit/master/content/articles/2023/2023-05-04_annonce-changement-url-site-geotribu.md",
        )

    def test_url_rm_query_parameters(self):
        """Test URL query params removal."""
        self.assertEqual(
            url_rm_query(
                in_url="https://geotribu.fr/rdp/2023/rdp_2023-05-12/?utm_campaign=feed-syndication&utm_medium=RSS&utm_source=rss-feed",
                param_startswith="utm_",
            ),
            "https://geotribu.fr/rdp/2023/rdp_2023-05-12/",
        )


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
