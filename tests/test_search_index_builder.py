#! python3

"""
Usage from the repo root folder:

.. code-block:: bash
    # for whole tests
    python -m unittest tests.test_search_index_builder
    # for specific test
    python -m unittest tests.test_search_index_builder.TestSearchIndexBuilder.test_get_page_url
"""

# standard library
import json
import tempfile
import unittest
from pathlib import Path

# 3rd party
from lunr.index import Index
from lunr.languages import get_nltk_builder

# project
from geotribu_cli import cli
from geotribu_cli.search.search_index_builder import (
    add_lunr_index,
    build_search_listing,
    create_markdown_parser,
    get_page_url,
    list_markdown_files,
)

# ############################################################################
# ########## Classes #############
# ################################


class TestSearchIndexBuilder(unittest.TestCase):
    """Test search index building from Markdown files."""

    def setUp(self):
        """Create a temporary folder of Markdown files."""
        temp_dir = tempfile.TemporaryDirectory(prefix="geotribu_search_index_")
        self.addCleanup(temp_dir.cleanup)
        self.docs = Path(temp_dir.name) / "docs"
        (self.docs / "articles").mkdir(parents=True)

    def write(self, relative_path: str, content: str = "# Titre\n"):
        """Write a file into the temporary docs folder."""
        file_path = self.docs / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")

    def get_docs(self, indexing: str = "full", **kwargs) -> dict[str, dict]:
        """Build documents from the temporary docs folder, by location."""
        listing = build_search_listing(
            docs_folder=self.docs,
            md_parser=create_markdown_parser(),
            languages=["fr"],
            indexing=indexing,
            **kwargs,
        )
        return {doc["location"]: doc for doc in listing["docs"]}

    # -- Files listing ---------------------------------------------------------

    def test_list_markdown_files_order_and_exclusions(self):
        """Index comes first, hidden files, templates and other formats are ignored."""
        for relative_path in (
            "zzz.md",
            "aaa.markdown",
            "index.md",
            "notes.txt",
            ".hidden.md",
            ".git/page.md",
            "templates/page.md",
            "articles/templates/page.md",
        ):
            self.write(relative_path)

        self.assertEqual(
            [
                path.relative_to(self.docs).as_posix()
                for path in list_markdown_files(self.docs)
            ],
            ["index.md", "aaa.markdown", "zzz.md", "articles/templates/page.md"],
        )

    def test_list_markdown_files_index_takes_over_readme(self):
        """In a folder, README is ignored if there is an index."""
        self.write("README.md")
        self.write("index.md")
        self.write("articles/README.md")

        self.assertEqual(
            [
                path.relative_to(self.docs).as_posix()
                for path in list_markdown_files(self.docs)
            ],
            ["index.md", "articles/README.md"],
        )

    # -- URLs ------------------------------------------------------------------

    def test_get_page_url(self):
        """Test URLs with and without directory URLs."""
        for relative_path, directory_url, file_url in (
            ("index.md", "", "index.html"),
            ("README.md", "", "index.html"),
            ("foo.md", "foo/", "foo.html"),
            ("foo/index.md", "foo/", "foo/index.html"),
            ("foo/README.md", "foo/", "foo/index.html"),
            ("foo/bar.md", "foo/bar/", "foo/bar.html"),
            (
                "été 1/a b.md",
                "%C3%A9t%C3%A9%201/a%20b/",
                "%C3%A9t%C3%A9%201/a%20b.html",
            ),
        ):
            with self.subTest(relative_path):
                self.assertEqual(get_page_url(relative_path), directory_url)
                self.assertEqual(
                    get_page_url(relative_path, use_directory_urls=False), file_url
                )

    # -- Documents -------------------------------------------------------------

    def test_documents_page_and_sections(self):
        """A page gets a document, plus a document by heading."""
        self.write(
            "articles/page.md",
            "---\ntitle: Titre YAML\n---\n\n# Titre H1\n\nIntro **grasse**.\n\n"
            "## Section&nbsp;A\n\nTexte  A.\n",
        )

        docs = self.get_docs()

        self.assertEqual(
            list(docs),
            [
                "articles/page/",
                "articles/page/#titre-h1",
                "articles/page/#section-a",
            ],
        )
        self.assertEqual(docs["articles/page/"]["title"], "Titre YAML")
        self.assertEqual(
            docs["articles/page/"]["text"],
            "Titre H1 Intro grasse . Section A Texte A.",
        )
        self.assertEqual(docs["articles/page/#titre-h1"]["title"], "Titre H1")
        self.assertEqual(docs["articles/page/#section-a"]["text"], "Texte A.")

    def test_documents_title_fallbacks(self):
        """Title: metadata, then H1 opening the page, then homepage or file name."""
        self.write("index.md", "Texte\n\n# H1 tardif\n")
        self.write("articles/mon_fichier-test.md", "Texte\n")
        self.write("articles/CamelCase.md", "Texte\n")
        self.write("articles/h1.md", "# H1 en tête\n")
        self.write("articles/yaml.md", "---\ntitle: [invalide\n---\n\n# H1 yaml\n")

        docs = self.get_docs()

        self.assertEqual(docs[""]["title"], "Home")
        self.assertEqual(
            docs["articles/mon_fichier-test/"]["title"], "Mon fichier test"
        )
        self.assertEqual(docs["articles/CamelCase/"]["title"], "CamelCase")
        self.assertEqual(docs["articles/h1/"]["title"], "H1 en tête")
        self.assertEqual(docs["articles/yaml/"]["title"], "Yaml")

    def test_documents_indexing_strategies(self):
        """Test full, sections and titles indexing."""
        self.write("page.md", "# Titre\n\nTexte\n\n## Section\n\nTexte\n")

        self.assertEqual(
            self.get_docs(indexing="full")["page/#section"]["text"], "Texte"
        )

        sections = self.get_docs(indexing="sections")
        self.assertEqual(len(sections), 3)
        self.assertEqual({doc["text"] for doc in sections.values()}, {""})

        titles = self.get_docs(indexing="titles")
        self.assertEqual(list(titles), ["page/"])
        self.assertEqual(titles["page/"]["text"], "")

    def test_unreadable_file_is_skipped(self):
        """A file which is not UTF-8 encoded does not prevent indexing other files."""
        self.write("ok.md")
        (self.docs / "latin1.md").write_bytes("# Été".encode("latin-1"))

        self.assertEqual(list(self.get_docs()), ["ok/", "ok/#titre"])

    def test_markdown_extensions(self):
        """Extensions are enabled in addition to the default ones."""
        self.write("page.md", "# Titre\n\nTexte\n{: .classe }\n")

        self.assertIn("{: .classe }", self.get_docs()["page/"]["text"])

        listing = build_search_listing(
            docs_folder=self.docs,
            md_parser=create_markdown_parser(["attr_list"]),
            languages=["fr"],
        )
        self.assertEqual(listing["docs"][0]["text"], "Titre Texte")

    # -- Lunr index ------------------------------------------------------------

    def test_add_lunr_index(self):
        """The prebuilt index can be loaded and searched."""
        self.write("cartes.md", "# Cartes\n\nDes chevaux sur une carte.\n")
        self.write("autre.md", "# Autre\n\nRien à voir.\n")

        listing = build_search_listing(
            docs_folder=self.docs,
            md_parser=create_markdown_parser(),
            languages=["fr"],
        )
        self.assertIs(listing["config"]["prebuild_index"], False)
        self.assertNotIn("index", listing)

        add_lunr_index(listing)
        self.assertEqual(listing["config"]["prebuild_index"], "python")

        get_nltk_builder(["fr"])
        results = Index.load(listing["index"]).search("chevaux")
        self.assertEqual(
            {result["ref"] for result in results}, {"cartes/", "cartes/#cartes"}
        )

    # -- CLI -------------------------------------------------------------------

    def test_cli_without_lunr_index(self):
        """The command writes a JSON file with Mkdocs structure and settings."""
        self.write("page.md")
        output_file = self.docs.parent / "sub" / "dir" / "search_index.json"

        cli.main(
            [
                "build-search-index",
                str(self.docs),
                "--output",
                str(output_file),
                "--lang",
                "fr",
                "--lang",
                "en",
                "--no-prebuild-index",
            ]
        )

        self.assertEqual(
            json.loads(output_file.read_text(encoding="utf-8")),
            {
                "config": {
                    "indexing": "full",
                    "lang": ["fr", "en"],
                    "min_search_length": 3,
                    "prebuild_index": False,
                    "separator": r"[\s\-]+",
                },
                "docs": [
                    {"location": "page/", "text": "Titre", "title": "Titre"},
                    {"location": "page/#titre", "text": "", "title": "Titre"},
                ],
            },
        )

    def test_cli_invalid_inputs(self):
        """The command exits with an error and writes nothing on invalid inputs."""
        output_file = self.docs.parent / "search_index.json"

        for label, args in (
            ("empty folder", [str(self.docs)]),
            ("missing folder", [str(self.docs / "nope")]),
            ("invalid extension", [str(self.docs), "-e", "extension_inconnue"]),
        ):
            with self.subTest(label), self.assertRaises(SystemExit) as context:
                cli.main(["bsi", *args, "-o", str(output_file)])
            self.assertEqual(context.exception.code, 1)
            self.assertFalse(output_file.exists())


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
