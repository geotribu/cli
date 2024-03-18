import argparse
import logging
import os
import shutil
import uuid
from datetime import datetime
from typing import Any

import requests
import yaml
from PIL import Image

from geotribu_cli.__about__ import __executable_name__, __version__
from geotribu_cli.constants import GeotribuDefaults
from geotribu_cli.content.json_feed import JsonFeedClient
from geotribu_cli.utils.dates_manipulation import is_more_recent

logger = logging.getLogger(__name__)
defaults_settings = GeotribuDefaults()

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


def check_publish_date(date: Any) -> bool:
    if isinstance(date, str):
        publish_date = datetime.strptime(date.split(" ")[0], "%Y-%m-%d").date()
    else:
        publish_date = date
    # TODO: check if date is another type and raise error
    return is_more_recent(datetime.now().date(), publish_date)


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


def check_tags(tags: list[str]) -> tuple[bool, set[str], set[str]]:
    existing_tags = get_existing_tags()
    all_exists = set(tags).issubset(existing_tags)
    missing = set(tags).difference(existing_tags)
    present = set(tags).intersection(existing_tags)
    return all_exists, missing, present


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

        # check that datetime is in the future
        if not check_publish_date(yaml_meta["date"]):
            msg = "La date de publication n'est pas dans le turfu !"
            logger.error(msg)
            if args.raise_exceptions:
                raise ValueError(msg)
        else:
            logger.info("Date de publication ok")

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
        all_exists, missing, _ = check_tags(yaml_meta["tags"])
        if not all_exists:
            msg = f"Les tags suivants n'existent pas dans les contenus Geotribu précédents : {','.join(missing)}"
            logger.error(msg)
            if args.raise_exceptions:
                raise ValueError(msg)
        else:
            logger.info("Tags ok")
