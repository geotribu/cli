#! python3  # noqa E265

"""
    Usage from the repo root folder:

    .. code-block:: bash
        # for whole tests
        python -m unittest tests.test_constants
        # for specific test
        python -m unittest tests.test_constants.TestConstants.test_geotribu_defaults
"""

# standard
import unittest

# 3rd party
import validators

# project
from geotribu_cli import constants

# ############################################################################
# ########## Classes #############
# ################################


class TestConstants(unittest.TestCase):
    """Test package static variables."""

    def test_geotribu_defaults(self):
        """Test types."""
        defaults_settings = constants.GeotribuDefaults()

        self.assertTrue(hasattr(defaults_settings, "git_base_url_organisation"))
        self.assertTrue(hasattr(defaults_settings, "site_base_url"))
        self.assertTrue(hasattr(defaults_settings, "site_git_project"))
        self.assertTrue(hasattr(defaults_settings, "site_search_index"))
        self.assertTrue(hasattr(defaults_settings, "cdn_base_url"))
        self.assertTrue(hasattr(defaults_settings, "cdn_base_path"))
        self.assertTrue(hasattr(defaults_settings, "cdn_search_index"))
        self.assertTrue(hasattr(defaults_settings, "comments_base_url"))
        self.assertTrue(hasattr(defaults_settings, "cdn_search_index_full_url"))
        self.assertTrue(hasattr(defaults_settings, "site_search_index_full_url"))

        self.assertIsInstance(defaults_settings.cdn_search_index_full_url, str)
        self.assertIsInstance(defaults_settings.site_search_index_full_url, str)
        self.assertTrue(validators.url(defaults_settings.cdn_search_index_full_url))
        self.assertTrue(validators.url(defaults_settings.site_search_index_full_url))


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
