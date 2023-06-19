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
from urllib.parse import unquote, urlsplit

# 3rd party
import tinify

# package
from geotribu_cli.console import console
from geotribu_cli.constants import GeotribuDefaults
from geotribu_cli.utils.check_path import check_path
from geotribu_cli.utils.start_uri import open_uri
from geotribu_cli.utils.str2bool import str2bool

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
    image_path_or_url: str | Path, image_type: str = "body"
) -> Path:
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
        output_filepath = defaults_settings.geotribu_working_folder.joinpath(
            f"images/optim/{img_filename}"
        )
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
        "--no-auto-open",
        "--stay",
        default=str2bool(getenv("GEOTRIBU_AUTO_OPEN_AFTER", True)),
        action="store_false",
        dest="opt_auto_open_disabled",
        help="Désactive l'ouverture automatique à la fin de la commande.",
    )

    subparser.add_argument(
        "-o",
        "--output-path",
        help="Fichier de sortie. Par défaut, stocke dans le dossier de travail local "
        "de Geotribu.",
        dest="output_path",
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
        "-w",
        "--with",
        choices=["tinypng"],
        default="tinypng",
        dest="tool_to_use",
        help="Outil à utiliser pour réaliser l'optimisation.",
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
    if args.tool_to_use == "tinypng":
        if not getenv("TINIFY_API_KEY"):
            logger.critical(
                "La clé d'API de Tinify n'est pas configurée en variable "
                "d'environnement 'TINIFY_API_KEY'."
            )
            sys.exit(1)

        if check_path(
            input_path=args.image_path,
            must_be_a_folder=True,
            must_be_a_file=False,
            must_be_readable=True,
            must_exists=True,
            raise_error=False,
        ):
            logger.info("Dossier d'images passé. L")
            li_images = [
                image.resolve()
                for image in Path(args.image_path).glob("*")
                if image.suffix.lower() in defaults_settings.images_body_extensions
            ]
            if not li_images:
                print(":person_shrugging: Aucune image trouvée dans {args.image_path}")
                sys.exit(0)
        else:
            li_images = [args.image_path]

        # optimize the image(s)
        count_optim_success = 0
        count_optim_error = 0
        for img in li_images:
            try:
                optimized_image = optimize_with_tinify(
                    image_path_or_url=img, image_type=args.image_type
                )
                console.print(
                    f":clamp: L'image {img} a été redimensionnée et "
                    f"compressée avec {args.tool_to_use} : {optimized_image}"
                )
                count_optim_success += 1
            except Exception as err:
                logger.error(
                    f"La compression de l'image {img} avec "
                    f"{args.tool_to_use} a échoué. Trace : {err}"
                )
                count_optim_error += 1

        # open output folder if success and not disabled
        if args.opt_auto_open_disabled and count_optim_success > 0:
            open_uri(
                in_filepath=defaults_settings.geotribu_working_folder.joinpath(
                    "images/optim"
                )
            )


# -- Stand alone execution
if __name__ == "__main__":
    pass
