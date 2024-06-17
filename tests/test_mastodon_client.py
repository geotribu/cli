"""
    Usage from the repo root folder:

    .. code-block:: bash
        # for whole tests
        python -m unittest tests.test_mastodon_client
        # for specific test
        python -m unittest tests.test_mastodon_client.TestCustomMastodonClient.test_export_data_all
"""

# standard
import unittest
from os import getenv
from pathlib import Path
from tempfile import TemporaryDirectory

# project
from geotribu_cli.__about__ import __title_clean__, __version__
from geotribu_cli.social.mastodon_client import ExtendedMastodonClient

# ############################################################################
# ########## Classes #############
# ################################


class TestCustomMastodonClient(unittest.TestCase):
    """Test package static variables."""

    def test_full_account_with_instance(self):
        """Test full account completion using a default instance."""
        self.assertEqual(
            ExtendedMastodonClient.full_account_with_instance(
                account={"acct": "datagouvfr@social.numerique.gouv.fr"}
            ),
            "datagouvfr@social.numerique.gouv.fr",
        )
        self.assertEqual(
            ExtendedMastodonClient.full_account_with_instance(
                account={"acct": "leaflet"}
            ),
            "leaflet@mapstodon.space",
        )
        self.assertEqual(
            ExtendedMastodonClient.full_account_with_instance(
                account={"acct": "opengisch"}, default_instance="fosstodon.org"
            ),
            "opengisch@fosstodon.org",
        )

    def test_instance_domain_from_url(self):
        """Test instance domain extraction from URL."""
        self.assertEqual(
            ExtendedMastodonClient.url_to_instance_domain(
                url="https://mapstodon.space/@geotribu"
            ),
            "mapstodon.space",
        )

    @unittest.skipIf(
        condition=getenv("GEOTRIBU_MASTODON_API_ACCESS_TOKEN") is None,
        reason="Le jeton d'API Mastodon est requis pour exécuter ce test.",
    )
    def test_export_data_all(self):
        """Test export following accounts to CSV."""
        print(getenv("GEOTRIBU_MASTODON_API_ACCESS_TOKEN"))
        masto_client = ExtendedMastodonClient(
            user_agent=f"{__title_clean__}-TESTS/{__version__}", debug_requests=False
        )
        with TemporaryDirectory(
            f"{__title_clean__}_{__version__}_tests_mastodon_"
        ) as tempo_dir:
            # export
            masto_client.export_data(
                dest_path_following_accounts=Path(tempo_dir).joinpath(
                    "following_accounts.csv"
                ),
                dest_path_lists=Path(tempo_dir).joinpath("lists.csv"),
                dest_path_lists_only_accounts=Path(tempo_dir).joinpath(
                    "lists_only_accounts.csv"
                ),
            )
            # checks
            self.assertTrue(Path(tempo_dir).joinpath("following_accounts.csv").exists())
            self.assertTrue(Path(tempo_dir).joinpath("lists.csv").exists())
            self.assertTrue(
                Path(tempo_dir).joinpath("lists_only_accounts.csv").exists()
            )

            self.assertGreater(
                Path(tempo_dir).joinpath("following_accounts.csv").stat().st_size, 0
            )
            self.assertGreater(Path(tempo_dir).joinpath("lists.csv").stat().st_size, 0)
            self.assertGreater(
                Path(tempo_dir).joinpath("lists_only_accounts.csv").stat().st_size, 0
            )


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
