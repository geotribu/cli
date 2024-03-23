import unittest
from unittest.mock import patch

import yaml

from geotribu_cli.content.header_check import check_publish_date, check_tags


class TestYamlHeaderCheck(unittest.TestCase):
    def setUp(self):
        with open("tests/fixtures/content/2012-12-21_article_passe.md") as past_file:
            past_content = past_file.read()
            _, front_matter, _ = past_content.split("---", 2)
            self.past_yaml_meta = yaml.safe_load(front_matter)

        with open("tests/fixtures/content/2044-04-01_article_futur.md") as future_file:
            future_content = future_file.read()
            _, front_matter, _ = future_content.split("---", 2)
            self.future_yaml_meta = yaml.safe_load(front_matter)

    def test_past_publish_date(self):
        self.assertFalse(check_publish_date(self.past_yaml_meta["date"]))

    def test_future_publish_date(self):
        self.assertTrue(check_publish_date(self.future_yaml_meta["date"]))

    @patch("geotribu_cli.content.header_check.get_existing_tags")
    def test_past_tags(self, get_existing_tags_mock):
        get_existing_tags_mock.return_value = ["QGIS", "OSM"]
        tags_ok, missing_tags, present_tags = check_tags(self.past_yaml_meta["tags"])
        self.assertFalse(tags_ok)
        self.assertIn("Fromage", missing_tags)
        self.assertIn("QGIS", present_tags)
        self.assertIn("OSM", present_tags)

    @patch("geotribu_cli.content.header_check.get_existing_tags")
    def test_future_tags(self, get_existing_tags_mock):
        get_existing_tags_mock.return_value = ["Fromage", "IGN"]
        tags_ok, missing_tags, present_tags = check_tags(self.future_yaml_meta["tags"])
        self.assertFalse(tags_ok)
        self.assertIn("QGIS", missing_tags)
        self.assertIn("OSM", missing_tags)
        self.assertIn("Fromage", present_tags)
        self.assertIn("IGN", present_tags)
