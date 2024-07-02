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

# package
from geotribu_cli.__about__ import __package_name__
from geotribu_cli.console import console
from geotribu_cli.constants import GeotribuDefaults
from geotribu_cli.images.optim_pillow import PILLOW_INSTALLED, pil_redimensionner_image
from geotribu_cli.images.optim_tinify import TINIFY_INSTALLED, optimize_with_tinify
from geotribu_cli.utils.check_path import check_path
from geotribu_cli.utils.start_uri import open_uri
from geotribu_cli.utils.str2bool import str2bool

# ############################################################################
# ########## GLOBALS #############
# ################################

logger = logging.getLogger(__name__)
defaults_settings = GeotribuDefaults()


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
        dest="output_path",
        help="Fichier de sortie. Par défaut, stocke dans le dossier de travail local "
        "de Geotribu.",
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
        choices=["local", "tinypng"],
        default=getenv("GEOTRIBU_DEFAULT_IMAGE_OPTIMIZER", "tinypng"),
        dest="tool_to_use",
        help="Outil à utiliser pour réaliser l'optimisation. Local (pillow), ou tinypng "
        "(service distant nécessitant une clé d'API)",
        metavar="GEOTRIBU_DEFAULT_IMAGE_OPTIMIZER",
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
    # dossier de sortie
    output_folder = Path(
        args.output_path
    ) or defaults_settings.geotribu_working_folder.joinpath("images/optim/")

    # liste l'image ou les images à optimiser
    if check_path(
        input_path=args.image_path,
        must_be_a_folder=True,
        must_be_a_file=False,
        must_be_readable=True,
        must_exists=True,
        raise_error=False,
    ):
        input_images_folder = Path(args.image_path).resolve()
        logger.info(f"Dossier d'images passé : {input_images_folder}")
        logger.info(f"Dossier en sortie : {output_folder}")
        li_images = [
            image.resolve()
            for image in input_images_folder.glob("*")
            if image.suffix.lower() in defaults_settings.images_body_extensions
        ]
        if not li_images:
            console.print(
                f":person_shrugging: Aucune image trouvée dans {args.image_path}"
            )
            sys.exit(0)
    else:
        logger.debug(f"Image unique passée : {args.image_path}")
        li_images = [Path(args.image_path)]

    # Utilise l'outil d'optimisation
    if args.tool_to_use == "tinypng":
        if not TINIFY_INSTALLED:
            logger.critical(
                "Tinify n'est pas installé, le service ne peut donc pas être utilisé. "
                "Pour l'utiliser, installer l'outil avec les dépendances "
                f"supplémentaires : pip install {__package_name__}[img-remote] ou "
                f"pip install {__package_name__}[all]"
            )
            sys.exit(1)

        if not getenv("TINIFY_API_KEY"):
            logger.critical(
                "La clé d'API de Tinify n'est pas configurée en variable "
                "d'environnement 'TINIFY_API_KEY'."
            )
            sys.exit(1)

        # optimize the image(s)
        count_optim_success = 0
        count_optim_error = 0
        for img in li_images:
            try:
                optimized_image = optimize_with_tinify(
                    image_path_or_url=img,
                    image_type=args.image_type,
                    output_folder=output_folder,
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
    elif args.tool_to_use == "local":
        if not PILLOW_INSTALLED:
            logger.critical(
                "Pillow n'est pas installé. "
                "Pour l'utiliser, installer l'outil avec les dépendances "
                f"supplémentaires : pip install {__package_name__}[img-local] ou "
                f"pip install {__package_name__}[all]"
            )
            sys.exit(1)

        # optimize the image(s)
        count_optim_success = 0
        count_optim_error = 0
        for img in li_images:
            try:
                optimized_image = pil_redimensionner_image(
                    image_path_or_url=img, output_folder=output_folder
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

    # report
    console.print(
        f":white_check_mark: {count_optim_success} image(s) correctement redimensionnée(s)\n"
        f":cross_mark: {count_optim_error} image(s) non redimensionnée(s)"
    )

    # open output folder if success and not disabled
    if args.opt_auto_open_disabled and count_optim_success > 0:
        open_uri(in_filepath=output_folder)
