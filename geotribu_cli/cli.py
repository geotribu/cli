#! python3  # noqa: E265

"""Main CLI entrypoint."""

# standard lib
import argparse
import logging
from typing import List

from rich_argparse import RawDescriptionRichHelpFormatter

# package
from geotribu_cli.__about__ import (
    __author__,
    __cli_usage__,
    __summary__,
    __title__,
    __title_clean__,
    __uri_homepage__,
    __version__,
)
from geotribu_cli.subcommands import (
    parser_latest_content,
    parser_search_content,
    parser_search_image,
    parser_upgrade,
)

RawDescriptionRichHelpFormatter.usage_markup = True


# ############################################################################
# ########## MAIN ################
# ################################

# this serves as a parent parser
def add_common_arguments(parser_to_update: argparse.ArgumentParser):
    """Apply common argument to an existing parser.

    Args:
        parser_to_update (argparse.ArgumentParser): _description_

    Returns:
        argparse.ArgumentParser: _description_
    """
    parser_to_update.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=1,
        dest="verbosity",
        help="Niveau de verbosité : None = WARNING, -v = INFO, -vv = DEBUG",
    )
    return parser_to_update


def main(args: List[str] = None):
    """Main CLI entrypoint.

    Args:
        args (List[str], optional): list of command-line arguments. Defaults to None.
    """
    # create the top-level parser
    main_parser = argparse.ArgumentParser(
        formatter_class=RawDescriptionRichHelpFormatter,
        epilog=f"{__cli_usage__}\n\n"
        f"Développé par {__author__}\n"
        f"Documentation : {__uri_homepage__}",
        description=f"{__title__} {__version__} - {__summary__}",
    )

    # -- ROOT ARGUMENTS --

    # Optional verbosity counter (eg. -v, -vv, -vvv, etc.)
    main_parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=1,
        dest="verbosity",
        help="Niveau de verbosité : None = WARNING, -v = INFO, -vv = DEBUG",
    )

    main_parser.add_argument(
        "--version",
        action="version",
        version=__version__,
        help="Affiche la version du CLI",
    )

    # -- SUB-COMMANDS --
    subparsers = main_parser.add_subparsers(title="Sous-commandes", dest="command")

    # Latest Content
    subcmd_latest_content = subparsers.add_parser(
        "read-latest",
        aliases=["latest", "rss"],
        help="Consulter les derniers contenus du site",
        formatter_class=main_parser.formatter_class,
        prog="read-latest",
    )
    add_common_arguments(subcmd_latest_content)
    parser_latest_content(subcmd_latest_content)

    # Search Content
    subcmd_search_content = subparsers.add_parser(
        "search-content",
        aliases=["contenus"],
        help="Rechercher dans les contenus du site",
        formatter_class=main_parser.formatter_class,
        prog="search-content",
    )
    add_common_arguments(subcmd_search_content)
    parser_search_content(subcmd_search_content)

    # Search Image
    subcmd_search_image = subparsers.add_parser(
        "search-image",
        aliases=["images"],
        help="Rechercher dans les images du CDN",
        formatter_class=main_parser.formatter_class,
        prog="search-image",
    )
    add_common_arguments(subcmd_search_image)
    parser_search_image(subcmd_search_image)

    # Upgrader
    subcmd_upgrade = subparsers.add_parser(
        "upgrade",
        aliases=["auto-update", "maj", "update"],
        help="Mettre à jour Geotribu CLI.",
        formatter_class=main_parser.formatter_class,
        prog="upgrade",
    )
    add_common_arguments(subcmd_upgrade)
    parser_upgrade(subcmd_upgrade)

    # just get passed args
    args = main_parser.parse_args(args)

    # set log level depending on verbosity argument
    if 0 < args.verbosity < 4:
        args.verbosity = 40 - (10 * args.verbosity)
    elif args.verbosity >= 4:
        # debug is the limit
        args.verbosity = 40 - (10 * 3)
    else:
        args.verbosity = 0

    logging.basicConfig(
        level=args.verbosity,
        format="%(asctime)s||%(levelname)s||%(module)s||%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler()
    console.setLevel(args.verbosity)

    # add the handler to the root logger
    logger = logging.getLogger(__title_clean__)
    logger.debug(f"Log level set: {logging.getLevelName(args.verbosity)}")

    # -- RUN LOGIC --
    args.func(args)


# -- Stand alone execution
if __name__ == "__main__":
    main()  # required by unittest
