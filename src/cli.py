#! python3  # noqa: E265

"""Main CLI entrypoint."""

# standard lib
import argparse
import logging
import sys
from datetime import datetime
from os import getenv
from pathlib import Path
from typing import List

# package
from src.__about__ import (
    __author__,
    __cli_usage__,
    __summary__,
    __title__,
    __title_clean__,
    __uri_homepage__,
    __version__,
)

# ############################################################################
# ########## MAIN ################
# ################################


def main(argv: List[str] = None):
    """Main CLI entrypoint."""
    # create the top-level parser
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"{__cli_usage__}\n\n"
        f"Développé avec \u2764\uFE0F par {__author__}\n"
        f"Documentation : {__uri_homepage__}",
        description=f"{__title__} {__version__} - {__summary__}",
    )

    # -- ROOT ARGUMENTS --

    # Optional verbosity counter (eg. -v, -vv, -vvv, etc.)
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=1,
        dest="verbosity",
        help="Verbosity level: None = WARNING, -v = INFO, -vv = DEBUG",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=__version__,
    )

    # -- PARSE PASSED ARGUMENTS --

    # get passed args and force print help if none
    # args = parser.parse_args(None if sys.argv[1:] else ["-h"])

    # just get passed args
    args = parser.parse_args(argv)

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


# -- Stand alone execution
if __name__ == "__main__":
    main()  # required by unittest
