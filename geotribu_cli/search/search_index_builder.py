#! python3

"""Build a search index from Markdown files, like the search plugin of Mkdocs 1.6.1."""

# ############################################################################
# ########## IMPORTS #############
# ################################

# standard library
import argparse
import logging
import os
import posixpath
import re
import sys
from collections.abc import Iterable, Iterator
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote

# 3rd party
import frontmatter
import orjson
from lunr.languages import SUPPORTED_LANGUAGES
from markdown import Markdown
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension
from markdown.extensions.toc import TocExtension
from yaml import YAMLError

# package
from geotribu_cli.console import console
from geotribu_cli.search.mdl_search import (
    MkdocsSearchConfiguration,
    MkdocsSearchDocument,
    MkdocsSearchListing,
)
from geotribu_cli.search.search_content import generate_index_from_docs
from geotribu_cli.utils.check_path import check_path
from geotribu_cli.utils.formatters import convert_octets

# ############################################################################
# ########## GLOBALS #############
# ################################

logger = logging.getLogger(__name__)

# same values as Mkdocs
HEADER_TAGS = ("h1", "h2", "h3", "h4", "h5", "h6")
MARKDOWN_SUFFIXES = (".markdown", ".mdown", ".mkdn", ".mkd", ".md")
SEARCH_MIN_LENGTH = 3
SEARCH_SEPARATOR = r"[\s\-]+"

# ############################################################################
# ########## CLASSES #############
# ################################


class ContentParser(HTMLParser):
    """Split a page HTML into its plain text and the sections under each heading."""

    def __init__(self) -> None:
        """Initialize the parser."""
        super().__init__()
        self.sections: list[tuple[str | None, list[str]]] = []
        self.stripped_html: list[str] = []
        self._in_heading = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Start a new section on each heading.

        Args:
            tag (str): tag name
            attrs (list[tuple[str, str | None]]): tag attributes
        """
        if tag in HEADER_TAGS:
            self._in_heading = True
            self.sections.append((dict(attrs).get("id"), []))

    def handle_endtag(self, tag: str) -> None:
        """Close the current heading.

        Args:
            tag (str): tag name
        """
        if tag in HEADER_TAGS:
            self._in_heading = False

    def handle_data(self, data: str) -> None:
        """Store text in the page and, out of headings, in the current section.

        Args:
            data (str): text
        """
        self.stripped_html.append(data)
        if self.sections and not self._in_heading:
            self.sections[-1][1].append(data.rstrip("\n"))


# ############################################################################
# ########## FUNCTIONS ###########
# ################################


def list_markdown_files(docs_folder: Path) -> Iterator[Path]:
    """List pages to index, in the same order and with the same exclusions as Mkdocs.

    Hidden files and folders and the root templates folder are ignored. In a folder,
    index and README come first and index takes over README.

    Args:
        docs_folder (Path): folder containing Markdown files

    Yields:
        Iterator[Path]: path to each page to index
    """
    for folder, subfolders, filenames in os.walk(docs_folder, followlinks=True):
        subfolders[:] = sorted(
            subfolder
            for subfolder in subfolders
            if not subfolder.startswith(".")
            and not (Path(folder) == docs_folder and subfolder == "templates")
        )

        pages: dict[str, Path] = {}
        for filename in sorted(
            filenames, key=lambda f: (Path(f).stem not in ("index", "README"), f)
        ):
            if filename.startswith(".") or not filename.endswith(MARKDOWN_SUFFIXES):
                continue

            stem = Path(filename).stem
            page_name = "index" if stem == "README" else stem
            if page_name in pages:
                logger.warning(
                    f"{pages[page_name]} ignoré car il est en conflit avec {filename}."
                )
            pages[page_name] = Path(folder) / filename

        yield from pages.values()


def get_page_url(relative_path: str, use_directory_urls: bool = True) -> str:
    """Determine the URL of a page, relative to the website root.

    Args:
        relative_path (str): POSIX path to the page, relative to the docs folder
        use_directory_urls (bool, optional): if True, `foo/bar.md` is served at
            `foo/bar/`. If False, at `foo/bar.html`. Defaults to True.

    Returns:
        str: page URL. Empty for the website homepage with directory URLs.
    """
    parent, filename = posixpath.split(relative_path)
    stem = posixpath.splitext(filename)[0]
    stem = "index" if stem == "README" else stem

    if not use_directory_urls:
        url = posixpath.join(parent, f"{stem}.html")
    elif stem == "index":
        url = f"{parent}/" if parent else ""
    else:
        url = f"{posixpath.join(parent, stem)}/"

    return quote(url)


def get_toc_titles(toc_tokens: Iterable[dict]) -> dict[str, str]:
    """Flatten a table of contents into a mapping of titles by heading ID.

    Args:
        toc_tokens (Iterable[dict]): tokens generated by the Markdown toc extension

    Returns:
        dict[str, str]: titles by heading ID
    """
    titles: dict[str, str] = {}
    for token in toc_tokens:
        titles[token["id"]] = token["name"]
        titles.update(get_toc_titles(token["children"]))
    return titles


def make_document(title: str, text: str, location: str) -> MkdocsSearchDocument:
    """Create a search document, normalizing whitespaces in its text.

    Args:
        title (str): page or section title
        text (str): page or section text
        location (str): page or section URL

    Returns:
        MkdocsSearchDocument: document to index
    """
    text = re.sub(r"[ \t\n\r\f\v]+", " ", text.replace("\u00a0", " ").strip())
    return {"title": title, "text": text, "location": location}


def build_page_documents(
    md_path: Path,
    docs_folder: Path,
    md_parser: Markdown,
    indexing: str = "full",
    use_directory_urls: bool = True,
) -> list[MkdocsSearchDocument]:
    """Build the search documents of a page.

    There is one document for the whole page, then one for each of its headings.

    Args:
        md_path (Path): path to the Markdown file
        docs_folder (Path): folder used as website root
        md_parser (Markdown): Markdown parser. Must have the toc extension enabled.
        indexing (str, optional): indexing strategy: full, sections or titles.
            Defaults to "full".
        use_directory_urls (bool, optional): see get_page_url. Defaults to True.

    Returns:
        list[MkdocsSearchDocument]: documents to index
    """
    source = md_path.read_text(encoding="utf-8-sig")
    try:
        metadata, markdown_text = frontmatter.parse(source)
    except YAMLError as err:
        logger.warning(f"Entête YAML de {md_path} ignorée car invalide. Trace : {err}")
        metadata, markdown_text = {}, source

    html = md_parser.reset().convert(markdown_text)
    toc_titles = get_toc_titles(getattr(md_parser, "toc_tokens", []))

    parser = ContentParser()
    parser.feed(html)
    parser.close()

    relative_path = md_path.relative_to(docs_folder).as_posix()
    url = get_page_url(relative_path, use_directory_urls)

    # title: metadata, then H1 if it opens the page, then homepage or file name
    title = metadata.get("title")
    if title is None and html.startswith("<h1") and parser.sections:
        title = toc_titles.get(parser.sections[0][0])
    if title is None and url in ("", "index.html"):
        title = "Home"
    if title is None:
        stem = "index" if md_path.stem == "README" else md_path.stem
        title = stem.replace("-", " ").replace("_", " ")
        title = title.capitalize() if title.lower() == title else title

    documents = [
        make_document(
            title=str(title),
            text="\n".join(parser.stripped_html) if indexing == "full" else "",
            location=url,
        )
    ]

    if indexing in ("full", "sections"):
        for section_id, section_text in parser.sections:
            if section_id in toc_titles:
                documents.append(
                    make_document(
                        title=toc_titles[section_id],
                        text=" ".join(section_text) if indexing == "full" else "",
                        location=f"{url}#{section_id}",
                    )
                )

    return documents


def create_markdown_parser(extensions: Iterable[str] = ()) -> Markdown:
    """Create a Markdown parser with the Mkdocs default extensions.

    Args:
        extensions (Iterable[str], optional): Markdown extensions to enable in addition
            to the default ones (toc, tables, fenced_code). Defaults to ().

    Returns:
        Markdown: Markdown parser
    """
    return Markdown(
        extensions=[
            TocExtension(),
            TableExtension(),
            FencedCodeExtension(),
            *extensions,
        ]
    )


def build_search_listing(
    docs_folder: Path,
    md_parser: Markdown,
    languages: list[str],
    indexing: str = "full",
    use_directory_urls: bool = True,
) -> MkdocsSearchListing:
    """Build the search configuration and documents from a folder of Markdown files.

    Args:
        docs_folder (Path): folder containing Markdown files
        md_parser (Markdown): Markdown parser. See create_markdown_parser.
        languages (list[str]): languages of the contents (ISO 639-1)
        indexing (str, optional): indexing strategy: full, sections or titles.
            Defaults to "full".
        use_directory_urls (bool, optional): see get_page_url. Defaults to True.

    Returns:
        MkdocsSearchListing: search configuration and documents
    """
    documents: list[MkdocsSearchDocument] = []
    for md_path in list_markdown_files(docs_folder):
        try:
            documents.extend(
                build_page_documents(
                    md_path=md_path,
                    docs_folder=docs_folder,
                    md_parser=md_parser,
                    indexing=indexing,
                    use_directory_urls=use_directory_urls,
                )
            )
        except (OSError, UnicodeDecodeError) as err:
            logger.warning(f"{md_path} ignoré car illisible. Trace : {err}")

    search_config: MkdocsSearchConfiguration = {
        "indexing": indexing,
        "lang": languages,
        "min_search_length": SEARCH_MIN_LENGTH,
        "prebuild_index": False,
        "separator": SEARCH_SEPARATOR,
    }

    return {"config": search_config, "docs": documents}


def add_lunr_index(listing: MkdocsSearchListing) -> None:
    """Add the prebuilt lunr index to a search listing.

    This is what Mkdocs does with its `prebuild_index: python` option.

    Args:
        listing (MkdocsSearchListing): search listing to update
    """
    listing["index"] = generate_index_from_docs(
        input_documents_to_index=listing["docs"],
        index_ref_id="location",
        index_configuration={"lang": listing["config"]["lang"]},
        index_fieds_definition=["title", "text"],
    ).serialize()
    listing["config"]["prebuild_index"] = "python"


# ############################################################################
# ########## CLI #################
# ################################


def parser_build_search_index(
    subparser: argparse.ArgumentParser,
) -> argparse.ArgumentParser:
    """Set the argument parser for build-search-index subcommand.

    Args:
        subparser (argparse.ArgumentParser): parser to set up

    Returns:
        argparse.ArgumentParser: parser ready to use
    """
    subparser.add_argument(
        "docs_folder",
        help="Dossier contenant les fichiers Markdown à indexer.",
        metavar="dossier",
        type=Path,
    )

    subparser.add_argument(
        "-o",
        "--output",
        default=Path("search_index.json"),
        dest="output_file",
        help="Fichier JSON à générer. Valeur par défaut : search_index.json",
        type=Path,
    )

    subparser.add_argument(
        "-l",
        "--lang",
        action="append",
        choices=sorted(SUPPORTED_LANGUAGES),
        dest="languages",
        help="Langue des contenus. Répéter l'option pour en indiquer plusieurs. "
        "Valeur par défaut : fr",
        metavar="LANGUE",
    )

    subparser.add_argument(
        "-i",
        "--indexing",
        choices=["full", "sections", "titles"],
        default="full",
        dest="indexing",
        help="Stratégie d'indexation : titres et textes (full), titres des pages et des "
        "sections (sections) ou titres des pages (titles).",
    )

    subparser.add_argument(
        "-e",
        "--markdown-extension",
        action="append",
        default=[],
        dest="markdown_extensions",
        help="Extension Python-Markdown à activer, en plus de toc, tables et "
        "fenced_code. Répéter l'option pour en indiquer plusieurs. Exemple : attr_list",
        metavar="EXTENSION",
    )

    subparser.add_argument(
        "--no-directory-urls",
        action="store_false",
        default=True,
        dest="use_directory_urls",
        help="Génère des URLs vers des fichiers (foo/bar.html) et non vers des dossiers "
        "(foo/bar/).",
    )

    subparser.add_argument(
        "--no-prebuild-index",
        action="store_false",
        default=True,
        dest="prebuild_index",
        help="N'ajoute pas l'index lunr précalculé : le fichier ne contient que la "
        "configuration et les documents.",
    )

    subparser.set_defaults(func=run)

    return subparser


# ############################################################################
# ########## MAIN ################
# ################################


def run(args: argparse.Namespace) -> None:
    """Run the sub command logic.

    Args:
        args (argparse.Namespace): arguments passed to the subcommand
    """
    logger.debug(f"Running {args.command} with {args}")

    if not check_path(
        input_path=args.docs_folder,
        must_exists=True,
        must_be_a_folder=True,
        must_be_readable=True,
        raise_error=False,
    ):
        logger.error(f"{args.docs_folder} n'est pas un dossier valide.")
        sys.exit(1)

    try:
        md_parser = create_markdown_parser(args.markdown_extensions)
    except (AttributeError, ImportError, TypeError, ValueError) as err:
        logger.error(f"Extension Markdown invalide. Trace : {err}")
        sys.exit(1)

    with console.status(
        f"Génère l'index de recherche de {args.docs_folder}...", spinner="earth"
    ):
        listing = build_search_listing(
            docs_folder=args.docs_folder,
            md_parser=md_parser,
            languages=args.languages or ["fr"],
            indexing=args.indexing,
            use_directory_urls=args.use_directory_urls,
        )

        if not listing["docs"]:
            logger.error(f"Aucun fichier Markdown trouvé dans {args.docs_folder}.")
            sys.exit(1)

        if args.prebuild_index:
            try:
                add_lunr_index(listing)
            except LookupError as err:
                logger.error(
                    "Les données NLTK (stopwords) requises par lunr sont indisponibles. "
                    f"Utiliser --no-prebuild-index pour s'en passer. Trace : {err}"
                )
                sys.exit(1)

    args.output_file.parent.mkdir(parents=True, exist_ok=True)
    with args.output_file.open(mode="wb") as fd:
        fd.write(orjson.dumps(listing, option=orjson.OPT_SORT_KEYS))

    console.print(
        f":white_check_mark: {len(listing['docs'])} documents indexés dans "
        f"{args.output_file} ({convert_octets(args.output_file.stat().st_size)})."
    )
