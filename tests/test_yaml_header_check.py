import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

from geotribu_cli.content.header_check import (
    check_author_md,
    check_existing_tags,
    check_image_extension,
    check_image_ratio,
    check_image_size,
    check_license,
    check_missing_mandatory_keys,
    check_tags_order,
    download_image_sizes,
)

# -- GLOBALS
TEAM_FOLDER = Path("tests/fixtures/team")
URL_TEST_VERTICAL_IMAGE = "https://cdn.geotribu.fr/img/articles-blog-rdp/articles/2024/mise_en_place_qfieldcloud_custom/screenshot_qfield_qfc_project.webp"
URL_TEST_HORIZONTAL_IMAGE = "https://cdn.geotribu.fr/img/articles-blog-rdp/capture-ecran/carte_trains_europe.png"


class TestYamlHeaderCheck(unittest.TestCase):
    image_sizes = download_image_sizes()

    def setUp(self):
        with open("tests/fixtures/content/2012-12-21_article_passe.md") as past_file:
            past_content = past_file.read()
            _, front_matter, _ = past_content.split("---", 2)
            self.past_yaml_meta = yaml.safe_load(front_matter)

        with open("tests/fixtures/content/2044-04-01_article_futur.md") as future_file:
            future_content = future_file.read()
            _, front_matter, _ = future_content.split("---", 2)
            self.future_yaml_meta = yaml.safe_load(front_matter)

    @patch("geotribu_cli.content.header_check.get_existing_tags")
    def test_past_tags_existence(self, get_existing_tags_mock):
        get_existing_tags_mock.return_value = ["QGIS", "OSM"]
        tags_ok, missing_tags, present_tags = check_existing_tags(
            self.past_yaml_meta["tags"]
        )
        self.assertFalse(tags_ok)
        self.assertIn("Fromage", missing_tags)
        self.assertIn("QGIS", present_tags)
        self.assertIn("OSM", present_tags)

    @patch("geotribu_cli.content.header_check.get_existing_tags")
    def test_future_tags_existence(self, get_existing_tags_mock):
        get_existing_tags_mock.return_value = ["Fromage", "IGN"]
        tags_ok, missing_tags, present_tags = check_existing_tags(
            self.future_yaml_meta["tags"]
        )
        self.assertFalse(tags_ok)
        self.assertIn("QGIS", missing_tags)
        self.assertIn("OSM", missing_tags)
        self.assertIn("Fromage", present_tags)
        self.assertIn("IGN", present_tags)

    def test_past_tags_order(self):
        self.assertTrue(check_tags_order(self.past_yaml_meta["tags"]))

    def test_future_tags_order(self):
        self.assertFalse(check_tags_order(self.future_yaml_meta["tags"]))

    def test_past_mandatory_keys(self):
        all_present, missing = check_missing_mandatory_keys(self.past_yaml_meta.keys())
        self.assertTrue(all_present)
        self.assertEqual(len(missing), 0)

    def test_future_mandatory_keys(self):
        all_present, missing = check_missing_mandatory_keys(
            self.future_yaml_meta.keys()
        )
        self.assertFalse(all_present)
        self.assertEqual(len(missing), 1)
        self.assertIn("description", missing)

    def test_author_md_ok(self):
        self.assertTrue(check_author_md("Jane Doe", TEAM_FOLDER))
        self.assertTrue(check_author_md("JaNe DoE", TEAM_FOLDER))
        self.assertTrue(check_author_md("Jàne Doe", TEAM_FOLDER))
        self.assertTrue(check_author_md("Jàne Döe", TEAM_FOLDER))
        self.assertTrue(check_author_md("Jàne Döé", TEAM_FOLDER))
        self.assertTrue(check_author_md("Jàne D'öé", TEAM_FOLDER))
        self.assertFalse(check_author_md("JaneDoe", TEAM_FOLDER))

    def test_license_ok(self):
        self.assertTrue(check_license(self.past_yaml_meta["license"]))

    def test_license_nok(self):
        self.assertFalse(check_license(self.future_yaml_meta["license"]))

    def test_image_extension_ok(self):
        self.assertTrue(check_image_extension("https://mon.image.png"))
        self.assertTrue(check_image_extension("https://mon.image.jpg"))
        self.assertTrue(check_image_extension("https://mon.image.jpeg"))

    def test_image_extension_nok(self):
        self.assertFalse(check_image_extension("https://mon.image.webp"))
        self.assertFalse(check_image_extension("https://mon.image.gif"))
        self.assertFalse(check_image_extension("https://mon.image.tiff"))

    def test_image_size_ok(self):
        self.assertTrue(
            check_image_size(
                URL_TEST_VERTICAL_IMAGE, self.image_sizes, max_width=800, max_height=800
            )
        )
        self.assertTrue(
            check_image_size(
                URL_TEST_HORIZONTAL_IMAGE,
                self.image_sizes,
                max_width=800,
                max_height=800,
            )
        )

    def test_image_size_nok(self):
        self.assertFalse(
            check_image_size(
                URL_TEST_VERTICAL_IMAGE, self.image_sizes, max_width=380, max_height=800
            )
        )
        self.assertFalse(
            check_image_size(
                URL_TEST_VERTICAL_IMAGE, self.image_sizes, max_width=800, max_height=799
            )
        )
        self.assertFalse(
            check_image_size(
                URL_TEST_HORIZONTAL_IMAGE,
                self.image_sizes,
                max_width=799,
                max_height=800,
            )
        )
        self.assertFalse(
            check_image_size(
                URL_TEST_HORIZONTAL_IMAGE,
                self.image_sizes,
                max_width=800,
                max_height=532,
            )
        )

    def test_image_ratio_ok(self):
        self.assertTrue(
            check_image_ratio(
                URL_TEST_VERTICAL_IMAGE, self.image_sizes, min_ratio=0.45, max_ratio=0.5
            )
        )
        self.assertTrue(
            check_image_ratio(
                URL_TEST_HORIZONTAL_IMAGE,
                self.image_sizes,
                min_ratio=1.45,
                max_ratio=1.55,
            )
        )
        self.assertTrue(
            check_image_ratio(
                URL_TEST_HORIZONTAL_IMAGE,
                self.image_sizes,
                min_ratio=1.49,
                max_ratio=1.51,
            )
        )

    def test_image_ratio_nok(self):
        self.assertFalse(
            check_image_ratio(
                URL_TEST_VERTICAL_IMAGE,
                self.image_sizes,
                min_ratio=1.45,
                max_ratio=1.55,
            )
        )
        self.assertFalse(
            check_image_ratio(
                URL_TEST_HORIZONTAL_IMAGE,
                self.image_sizes,
                min_ratio=1.2,
                max_ratio=1.3,
            )
        )
