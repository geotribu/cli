#! python3  # noqa E265

"""
    Usage from the repo root folder:

    .. code-block:: bash
        # for whole tests
        python -m unittest tests.test_utils_proxies
        # for specific test
        python -m unittest tests.test_utils_proxies.TestUtilsProxy.test_proxy_settings
"""

# standard library
import unittest
from os import environ

# project
from geotribu_cli.utils.proxies import get_proxy_settings

# ############################################################################
# ########## Classes #############
# ################################


class TestUtilsProxy(unittest.TestCase):
    """Test package utilities."""

    def test_proxy_settings(self):
        """Test proxy settings retriever."""
        # OK
        self.assertIsNone(get_proxy_settings())
        environ["HTTP_PROXY"] = "http://proxy.example.com:3128"
        self.assertIsInstance(get_proxy_settings(), dict)


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
