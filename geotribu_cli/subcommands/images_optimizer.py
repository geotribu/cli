#! python3  # noqa: E265

# ############################################################################
# ########## IMPORTS #############
# ################################

# standard library
import argparse
import logging
import sys
from os import getenv
from pathlib import Path

# 3rd party
import tinify

# package
from geotribu_cli.constants import GeotribuDefaults

# ############################################################################
# ########## GLOBALS #############
# ################################

logger = logging.getLogger(__name__)
defaults_settings = GeotribuDefaults()


# ############################################################################
# ########## FUNCTIONS ###########
# ################################


def tinify_check_api_limit() -> int:
    """Check the API limit and log it.

    Returns:
        compressions already done this month
    """
    tinify_api_limit = getenv("TINIFY_API_LIMIT", 500)
    compressions_this_month = tinify.compression_count
    # check if limit is reached
    if compressions_this_month and compressions_this_month >= tinify_api_limit:
        msg_exceeded_calls = (
            "Limite mensuelle d'appels à l'API Tinify atteinte : "
            f"{compressions_this_month}/{tinify_api_limit}. Attendre le "
            "mois prochain pour la Remise à zéro du quota ou utiliser une autre clé "
            "d'API."
        )
        logger.critical(msg=msg_exceeded_calls)
        sys.exit(1)

    return compressions_this_month


def optimize_with_tinify(image_path: Path) -> Path:
    """Optimize image using Tinify API (tinypng.com).

    Args:
        image_path: image to optimize

    Returns:
        path to the optimized image
    """
    # check API consumption
    tinify_check_api_limit()


# ############################################################################
# ########## CLI #################
# ################################


def parser_images_optimizer(
    subparser: argparse.ArgumentParser,
) -> argparse.ArgumentParser:
    """Set the argument parser for subcommand.

    Args:
        subparser (argparse.ArgumentParser): parser to set up

    Returns:
        argparse.ArgumentParser: parser ready to use
    """

    subparser.add_argument(
        "image_path",
        help="Chemin ou URL de l'image à optimiser ou chemin vers un dossier local.",
        type=str,
        metavar="image-path",
    )

    subparser.add_argument(
        "-t",
        "--to",
        choices=["body", "header", "icon"],
        default="body",
        dest="image_type",
        help="Usage auquel est destinée l'image : corps de texte (body), en-tête et "
        "partage (header), icône/logo (icon).",
    )

    subparser.add_argument(
        "-o",
        "--output-path",
        help="Fichier de sortie. Par défaut, stocke dans le dossier de travail local "
        "de Geotribu.",
        dest="output_path",
    )

    subparser.set_defaults(func=run)

    return subparser


# ############################################################################
# ########## MAIN ################
# ################################


def run(args: argparse.Namespace):
    """Run the sub command logic.

    Optimize image to fit .

    Args:
        args (argparse.Namespace): arguments passed to the subcommand
    """
    logger.debug(f"Running {args.command} with {args}")

    # check Tinify API KEY
    if not getenv("TINIFY_API_KEY"):
        logger.critical(
            "La clé d'API de Tinify n'est pas configurée en variable "
            "d'environnement 'TINIFY_API_KEY'."
        )
        sys.exit(1)

    tinify.key = getenv("TINIFY_API_KEY")
    logger.info(f"Clé d'API Tinify utilisée : {tinify.key[:5]}...")


# -- Stand alone execution
if __name__ == "__main__":
    pass
