#! python3  # noqa: E265

# ############################################################################
# ########## IMPORTS #############
# ################################

# standard library
import argparse
import logging
import re
import sys
from os import getenv

# 3rd party
import frontmatter
from rich.markdown import Markdown

# package
from geotribu_cli.console import console
from geotribu_cli.constants import GeotribuDefaults
from geotribu_cli.history import CliHistory
from geotribu_cli.utils.file_downloader import download_remote_file_to_local
from geotribu_cli.utils.formatters import (
    url_add_utm,
    url_content_name,
    url_content_source,
)
from geotribu_cli.utils.start_uri import open_uri

# ############################################################################
# ########## GLOBALS #############
# ################################

logger = logging.getLogger(__name__)
defaults_settings = GeotribuDefaults()

# regex
attr_list_pattern = r"{:[^}]*}"

# ############################################################################
# ########## FUNCTIONS ###########
# ################################


def open_content(content_uri: str, application: str = "shell"):
    """Open content in the selected application.

    Args:
        content_uri: URI to the content
        application: application to open content with. Defaults to "shell".
    """
    if application == "shell" and content_uri.startswith(
        defaults_settings.site_base_url
    ):
        local_file_path = download_remote_file_to_local(
            remote_url_to_download=url_content_source(in_url=content_uri, mode="raw"),
            local_file_path=defaults_settings.geotribu_working_folder.joinpath(
                f"remote/{url_content_name(url_content_source(content_uri, mode='raw'))}"
            ),
            content_type="text/plain; charset=utf-8",
        )

        with local_file_path.open(mode="rt", encoding="utf-8") as markdown_file:
            markdown_body = frontmatter.loads(markdown_file.read())

        markdown = Markdown(
            re.sub(attr_list_pattern, "", markdown_body.content, flags=re.DOTALL),
            hyperlinks=True,
        )
        console.print(markdown, emoji=True)

    elif application == "app" and content_uri.startswith("http"):
        open_uri(url_add_utm(content_uri))
    else:
        open_uri(content_uri)


# ############################################################################
# ########## CLI #################
# ################################


def parser_open_result(
    subparser: argparse.ArgumentParser,
) -> argparse.ArgumentParser:
    """Set the argument parser for subcommand.

    Args:
        subparser (argparse.ArgumentParser): parser to set up

    Returns:
        argparse.ArgumentParser: parser ready to use
    """

    subparser.add_argument(
        "result_index",
        help="Numéro du résultat précédent à ouvrir. Valeur par défault : 0.",
        metavar="result-index",
        default=1,
        type=int,
        nargs="?",
    )

    subparser.add_argument(
        "-w",
        "--with",
        choices=[
            "app",
            "shell",
        ],
        default=getenv("GEOTRIBU_OPEN_WITH", "shell"),
        dest="open_with",
        help="Avec quoi ouvrir le résultat : dans le terminal (shell) ou dans "
        "l'application correspondante au type de contenu (app). "
        "Valeur par défault : 'shell'.",
        metavar="GEOTRIBU_OPEN_WITH",
    )

    subparser.set_defaults(func=run)

    return subparser


# ############################################################################
# ########## MAIN ################
# ################################


def run(args: argparse.Namespace):
    """Run the sub command logic.

    Open result of a previous command.

    Args:
        args (argparse.Namespace): arguments passed to the subcommand
    """
    logger.debug(f"Running {args.command} with {args}")

    # local vars
    history = CliHistory()

    result_uri: str = history.load(result_index=args.result_index)
    if result_uri is None:
        sys.exit(0)

    print(f"Ouverture du résultat précédent n°{args.result_index} : {result_uri}")

    open_content(content_uri=result_uri, application=args.open_with)
