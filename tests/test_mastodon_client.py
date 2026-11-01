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
from types import SimpleNamespace
from unittest.mock import PropertyMock, patch

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

    def test_init_defaults_and_overrides(self):
        """Test CLI defaults are applied and can be overridden."""
        client = ExtendedMastodonClient(
            access_token=" " + "x" * 30 + " ", version_check_mode="none"
        )
        self.assertEqual(client.access_token, "x" * 30)
        self.assertEqual(client.request_timeout, 60)
        self.assertEqual(client.lang, "fr")
        self.assertEqual(client.api_base_url, "https://mapstodon.space")
        self.assertTrue(client.user_agent.startswith(f"{__title_clean__}/"))

        client = ExtendedMastodonClient(
            access_token="x" * 30, version_check_mode="none", request_timeout=5
        )
        self.assertEqual(client.request_timeout, 5)

    def test_comment_already_broadcasted_filters_statuses(self):
        """Test statuses without both hashtags or comment id are ignored."""
        client = ExtendedMastodonClient(
            access_token="x" * 30, version_check_mode="none"
        )
        tags = [{"name": "geotribot"}, {"name": "commentaire"}]
        relayed = {
            "url": "https://example.org/1",
            "tags": tags,
            "content": "comment-123",
        }
        # statuses already in memory: no API call
        client.my_statuses = [
            {"url": "https://example.org/2", "tags": None, "content": "comment-321"},
            {
                "url": "https://example.org/3",
                "tags": tags[:1],
                "content": "comment-321",
            },
            {"url": "https://example.org/4", "tags": tags, "content": "pas d'id"},
            relayed,
        ]

        self.assertIsNone(client.comment_already_broadcasted(321))
        self.assertEqual(client.comment_already_broadcasted(123), relayed)

    def test_comment_to_media_fits_instance_limit(self):
        """Test formatted comment never exceeds the instance limit."""
        client = ExtendedMastodonClient(
            access_token="x" * 30, version_check_mode="none"
        )
        comment = SimpleNamespace(
            id=1234,
            author="Jean-Michel",
            url_to_comment="https://geotribu.fr/articles/2026/un-article/#isso-1234",
            markdownified_text="mot " * 300,
        )
        with patch.object(
            ExtendedMastodonClient, "max_status_length", new_callable=PropertyMock
        ) as mock_max_length:
            for limit in (300, 500, 5000):
                mock_max_length.return_value = limit
                status = client.comment_to_media(in_comment=comment)
                self.assertLessEqual(client.get_status_length(status), limit)
                self.assertTrue(status.endswith("comment-1234"))

    @unittest.skipIf(
        condition=not getenv("GEOTRIBU_MASTODON_API_ACCESS_TOKEN"),
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
