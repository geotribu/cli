import argparse
import logging
import os
import shutil
import uuid

import requests
import yaml
from PIL import Image

from geotribu_cli.__about__ import __executable_name__, __version__
from geotribu_cli.constants import GeotribuDefaults
from geotribu_cli.content.json_feed import JsonFeedClient

logger = logging.getLogger(__name__)
defaults_settings = GeotribuDefaults()

MANDATORY_KEYS = [
    "title",
    "subtitle",
    "authors",
    "categories",
    "date",
    "description",
    "icon",
    "license",
    "tags",
]

# ############################################################################
# ########## CLI #################
# ################################


def parser_header_check(
    subparser: argparse.ArgumentParser,
) -> argparse.ArgumentParser:
    """Set the argument parser subcommand.

    Args:
        subparser (argparse.ArgumentParser): parser to set up

    Returns:
        argparse.ArgumentParser: parser ready to use
    """
    subparser.add_argument(
        "content_path",
        help="Chemin du fichier markdown dont l'entête est à vérifier",
        type=str,
        metavar="content",
    )
    subparser.add_argument(
        "-minr",
        "--min-ratio",
        dest="min_image_ratio",
        default=1.2,
        help="Ratio width/height minimum de l'image à vérifier",
    )
    subparser.add_argument(
        "-maxr",
        "--max-ratio",
        dest="max_image_ratio",
        default=1.5,
        help="Ratio width/height maximum de l'image à vérifier",
    )
    subparser.add_argument(
        "-r",
        "--raise",
        dest="raise_exceptions",
        action="store_true",
        default=False,
        help="Lever des exceptions et donc arrêter le programme si des erreurs sont rencontrées",
    )
    subparser.set_defaults(func=run)
    return subparser


# ############################################################################
# ########## MAIN ################
# ################################


def check_image_ratio(image_url: str, min_ratio: float, max_ratio: float) -> bool:
    r = requests.get(
        image_url,
        headers={"User-Agent": f"{__executable_name__}v{__version__}"},
        stream=True,
    )
    r.raise_for_status()
    image_file_name = str(uuid.uuid4())
    with open(image_file_name, "wb") as image_file:
        r.raw.decode_content = True
        try:
            shutil.copyfileobj(r.raw, image_file)
            with Image.open(image_file_name) as image:
                width, height = image.width, image.height
                ratio = width / height
                return min_ratio <= ratio <= max_ratio
        finally:
            os.remove(image_file_name)


def get_existing_tags() -> set[str]:
    jfc = JsonFeedClient()
    return jfc.get_tags(should_sort=True)


def check_existing_tags(tags: list[str]) -> tuple[bool, set[str], set[str]]:
    existing_tags = get_existing_tags()
    all_exists = set(tags).issubset(existing_tags)
    missing = set(tags).difference(existing_tags)
    present = set(tags).intersection(existing_tags)
    return all_exists, missing, present


def check_tags_order(tags: list[str]) -> bool:
    for i in range(len(tags) - 1):
        if tags[i] > tags[i + 1]:
            return False
    return True


def check_mandatory_keys(
    keys: list[str], mandatory: list[str] = MANDATORY_KEYS
) -> tuple[bool, set[str]]:
    missing = set()
    for mk in mandatory:
        if mk not in keys:
            missing.add(mk)
    return len(missing) == 0, missing


def run(args: argparse.Namespace) -> None:
    """Run the sub command logic.

    Checks YAML header of a content

    Args:
        args (argparse.Namespace): arguments passed to the subcommand
    """
    logger.debug(f"Running {args.command} with {args}")
    content_path = args.content_path

    if not os.path.exists(content_path):
        raise ValueError(f"Mayday ! Le fichier {content_path} n'existe pas !")

    with open(content_path) as file:
        content = file.read()
        _, front_matter, _ = content.split("---", 2)
        yaml_meta = yaml.safe_load(front_matter)
        logger.debug(f"YAML metadata loaded : {yaml_meta}")

        # check that image ratio is okayyy
        if "image" in yaml_meta:
            if not check_image_ratio(
                yaml_meta["image"], args.min_image_ratio, args.max_image_ratio
            ):
                msg = f"Le ratio de l'image n'est pas dans l'interface autorisé ({args.minratio} - {args.maxratio})"
                logger.error(msg)
                if args.raise_exceptions:
                    raise ValueError(msg)
            else:
                logger.info("Ratio image ok")

        # check that tags already exist
        all_exists, missing, _ = check_existing_tags(yaml_meta["tags"])
        if not all_exists:
            msg = f"Les tags suivants n'existent pas dans les contenus Geotribu précédents : {','.join(missing)}"
            logger.error(msg)
            if args.raise_exceptions:
                raise ValueError(msg)
        else:
            logger.info("Existence des tags ok")

        # check if tags are alphabetically sorted
        if not check_tags_order(yaml_meta["tags"]):
            msg = "Les tags ne sont pas triés par ordre alphabétique"
            logger.error(msg)
            if args.raise_exceptions:
                raise ValueError(msg)
        else:
            logger.info("Ordre alphabétique des tags ok")

        # check that mandatory keys are present
        all_present, missing = check_mandatory_keys(yaml_meta.keys(), MANDATORY_KEYS)
        if not all_present:
            msg = f"Les clés suivantes ne sont pas présentes dans l'entête markdown : {','.join(missing)}"
            logger.error(msg)
            if args.raise_exceptions:
                raise ValueError(msg)
        else:
            logger.info("Clés de l'entête ok")
