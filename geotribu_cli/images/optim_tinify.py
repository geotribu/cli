#! python3  # noqa: E265

# ############################################################################
# ########## IMPORTS #############
# ################################

# standard library
import logging
import sys
from os import getenv
from pathlib import Path
from typing import Optional, Union
from urllib.parse import unquote, urlsplit

# 3rd party
try:
    import tinify

    TINIFY_INSTALLED = True
except ImportError:
    TINIFY_INSTALLED = False

# package
from geotribu_cli.constants import GeotribuDefaults
from geotribu_cli.utils.check_path import check_path

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


def optimize_with_tinify(
    image_path_or_url: Union[str, Path], output_folder: Path, image_type: str = "body"
) -> Optional[Path]:
    """Optimize image using Tinify API (tinypng.com).

    Args:
        image_path_or_url: path or URL to the image to optimize
        image_type: type of image. Defaults to body.

    Returns:
        path to the optimized image
    """
    # check tinify credentials
    if not getenv("TINIFY_API_KEY"):
        logger.critical(
            "La clé d'API de Tinify n'est pas configurée en variable "
            "d'environnement 'TINIFY_API_KEY'."
        )
        sys.exit(1)

    tinify.key = getenv("TINIFY_API_KEY")

    # check API consumption
    tinify_check_api_limit()

    try:
        if isinstance(image_path_or_url, str) and image_path_or_url.startswith("https"):
            img_source = tinify.from_url(image_path_or_url)
            img_filename = unquote(urlsplit(image_path_or_url).path.split("/")[-1])

        else:
            if check_path(
                input_path=image_path_or_url,
                must_be_a_file=True,
                must_be_a_folder=False,
                must_be_readable=True,
            ):
                image_path_or_url = Path(image_path_or_url)

            img_source = tinify.from_file(str(image_path_or_url.resolve()))
            img_filename = image_path_or_url.name

        # preserve some metadata
        img_source_preserved = img_source.preserve("copyright", "creation")

        # scale it
        resized = img_source_preserved.resize(
            method="scale",
            width=1000,
        )

        # prepare output path
        output_filepath = output_folder.joinpath(f"{img_filename}")
        output_filepath.parent.mkdir(parents=True, exist_ok=True)

        # save output
        resized.to_file(str(output_filepath.resolve()))

        return output_filepath
    except tinify.AccountError as error:
        logger.critical(f"Account error: {error}")
        exit("Account error. Check your API key!")
    except tinify.ClientError as error:
        logger.error(f"Client error: {error}. Ignoring {image_path_or_url}.")
    except tinify.ServerError as error:
        logger.critical(f"Server error: {error}")
        exit("Server error. Check the log!")
    except tinify.ConnectionError as error:
        logger.critical(f"Connection error: {error}")
        exit("Connection error. Check the log!")
    except tinify.Error as error:
        logger.error(f"Error: {error}")
