#! python3  # noqa: E265

# ############################################################################
# ########## IMPORTS #############
# ################################

# standard library
import argparse
import logging
import re
from os import getenv

import frontmatter

# 3rd party
from openai import OpenAI
from rich.markdown import Markdown

# package
from geotribu_cli.console import console
from geotribu_cli.constants import GeotribuDefaults
from geotribu_cli.utils.file_downloader import download_remote_file_to_local
from geotribu_cli.utils.formatters import url_content_name, url_content_source

# ############################################################################
# ########## GLOBALS #############
# ################################

logger = logging.getLogger(__name__)
defaults_settings = GeotribuDefaults()

# regex
attr_list_pattern = r"{:[^}]*}"

# ############################################################################
# ########## CLI #################
# ################################


def parser_ia_summarize(
    subparser: argparse.ArgumentParser,
) -> argparse.ArgumentParser:
    """Set the argument parser for subcommand.

    Args:
        subparser (argparse.ArgumentParser): parser to set up

    Returns:
        argparse.ArgumentParser: parser ready to use
    """
    subparser.add_argument(
        "url_content",
        help="URL de l'article à résumer.",
        metavar="url_content",
        type=str,
    )

    subparser.add_argument(
        "-m",
        "--max-chars",
        help="Nombre de caractères maximum pour le résumé.",
        metavar="max_chars",
        default=500,
        type=int,
    )

    subparser.set_defaults(func=run)

    return subparser


# ############################################################################
# ########## MAIN ################
# ################################


def run(args: argparse.Namespace):
    """Run the sub command logic.

    Content summarizer.

    Args:
        args (argparse.Namespace): arguments passed to the subcommand
    """
    logger.debug(f"Running {args.command} with {args}")

    client = OpenAI(
        # This is the default and can be omitted
        api_key=getenv("OPENAI_API_KEY"),
    )

    client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Say this is a test",
            }
        ],
        model="gpt-3.5-turbo",
    )
    local_file_path = download_remote_file_to_local(
        remote_url_to_download=url_content_source(in_url=args.url_content, mode="raw"),
        local_file_path=defaults_settings.geotribu_working_folder.joinpath(
            f"remote/{url_content_name(in_url=url_content_source(in_url=args.url_content, mode='raw'))}"
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


# -- Stand alone execution
if __name__ == "__main__":
    pass
