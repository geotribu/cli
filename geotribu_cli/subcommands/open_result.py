#! python3  # noqa: E265

# ############################################################################
# ########## IMPORTS #############
# ################################

# standard library
import argparse
import logging
import sys
from os import getenv

# 3rd party
from rich.console import Console

# package
from geotribu_cli.constants import GeotribuDefaults
from geotribu_cli.history import CliHistory
from geotribu_cli.utils.start_uri import open_uri

# ############################################################################
# ########## GLOBALS #############
# ################################

logger = logging.getLogger(__name__)
defaults_settings = GeotribuDefaults()


# ############################################################################
# ########## FUNCTIONS ###########
# ################################


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
        help="Numéro du résultat précédent à ouvrir. Valeur par défault : 1.",
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

    Open .

    Args:
        args (argparse.Namespace): arguments passed to the subcommand
    """
    logger.debug(f"Running {args.command} with {args}")

    # local vars
    console = Console(record=True)
    history = CliHistory()

    result_uri: str = history.load(result_index=args.result_index)
    if result_uri is None:
        sys.exit(0)

    console.print(
        f"Ouverture du résultat précédent n°{args.result_index} : {result_uri}"
    )

    if args.open_with == "app":
        open_uri(result_uri)


# -- Stand alone execution
if __name__ == "__main__":
    pass
