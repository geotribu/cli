import unittest

from geotribu_cli.json.json_client import JsonFeedClient


class TestJsonClient(unittest.TestCase):
    """Test Geotribu JSON client."""

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.client = JsonFeedClient()
        self.items = self.client.items()
        self.tags = self.client.tags()

    def test_items_exist(self):
        self.assertGreater(len(self.items), 0)
        self.assertEqual(len(self.items), 50)

    def test_tags_exist(self):
        self.assertGreater(len(self.tags), 0)

    def test_some_existing_tags(self):
        for tag in ["OpenLayers", "QGIS", "OpenStreetMap", "QFieldCloud"]:
            self.assertIn(tag, self.tags)

    def test_unexisting_tags(self):
        for tag in ["Kinkeliba", "Jogging", "cziygiyezrvcyryez"]:
            self.assertNotIn(tag, self.tags)

    def test_sorted_tags(self):
        sorted_tags = self.client.tags(should_sort=True)
        i = 1
        while i < len(sorted_tags):
            if sorted_tags[i] < sorted_tags[i - 1]:
                raise Exception("Tags are not alphabetically sorted")
            i += 1
