import argparse
import logging
import os
import shutil
import uuid
from pathlib import Path

import frontmatter
import requests
from PIL import Image
from unidecode import unidecode

from geotribu_cli.__about__ import __executable_name__, __version__
from geotribu_cli.constants import GeotribuDefaults
from geotribu_cli.json.json_client import JsonFeedClient
from geotribu_cli.utils.check_path import check_path_exists

logger = logging.getLogger(__name__)
defaults_settings = GeotribuDefaults()

MANDATORY_KEYS = [
    "title",
    "authors",
    "categories",
    "date",
    "description",
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
        nargs="+",
    )
    subparser.add_argument(
        "-af",
        "--authors-folder",
        dest="authors_folder",
        type=Path,
        help="Chemin qui contient les presentations markdown des auteurs/autrices",
    )
    subparser.add_argument(
        "-minw",
        "--min-width",
        dest="min_image_width",
        default=400,
        type=int,
        help="Largeur minimum de l'image à vérifier",
    )
    subparser.add_argument(
        "-maxw",
        "--max-width",
        dest="max_image_width",
        default=800,
        type=int,
        help="Largeur maximum de l'image à vérifier",
    )
    subparser.add_argument(
        "-minh",
        "--min-height",
        dest="min_image_height",
        default=400,
        type=int,
        help="Hauteur minimum de l'image à vérifier",
    )
    subparser.add_argument(
        "-maxh",
        "--max-height",
        dest="max_image_height",
        default=800,
        type=int,
        help="Hauteur maximum de l'image à vérifier",
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


def check_author_md(author: str, folder: Path) -> bool:
    p = os.path.join(folder, f"{author.lower().replace(' ', '-')}.md")
    return os.path.exists(p)


def check_image_size(
    image_url: str, minw: int, maxw: int, minh: int, maxh: int
) -> bool:
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
                return minw <= image.width <= maxw and minh <= image.height <= maxh
            # return check_image_dimensions(
            #     Path(image_file_name),
            #     min_width=minw,
            #     max_width=maxw,
            #     min_height=minh,
            #     max_height=maxh,
            #     allowed_images_extensions=(".jpg", ".jpeg", ".png", ".webp")
            # )
        finally:
            os.remove(image_file_name)


def get_existing_tags() -> list[str]:
    jfc = JsonFeedClient()
    return jfc.tags(should_sort=True)


def check_existing_tags(tags: list[str]) -> tuple[bool, set[str], set[str]]:
    existing_tags = get_existing_tags()
    all_exists = set(tags).issubset(existing_tags)
    missing = set(tags).difference(existing_tags)
    present = set(tags).intersection(existing_tags)
    return all_exists, missing, present


def check_tags_order(tags: list[str]) -> bool:
    for i in range(len(tags) - 1):
        if unidecode(tags[i].upper()) > unidecode(tags[i + 1].upper()):
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
    content_paths = args.content_path

    for content_path in content_paths:
        logger.info(f"Checking header of {content_path}")
        check_path_exists(content_path, raise_error=True)

        with open(content_path) as file:
            content = frontmatter.load(file)
            yaml_meta = content.metadata
            logger.debug(f"YAML metadata loaded : {yaml_meta}")

            # check that image ratio is okayyy
            if "image" in yaml_meta:
                if not yaml_meta["image"]:
                    logger.error("Pas d'URL pour l'image")
                elif not check_image_size(
                    yaml_meta["image"],
                    args.min_image_width,
                    args.max_image_width,
                    args.min_image_height,
                    args.max_image_height,
                ):
                    msg = (
                        f"Les dimensions de l'image ne sont pas dans l'intervalle autorisé "
                        f"(w:{args.min_image_width}-{args.max_image_width},"
                        f"h:{args.min_image_height}-{args.max_image_height})"
                    )
                    logger.error(msg)
                    if args.raise_exceptions:
                        raise ValueError(msg)
                else:
                    logger.info("Ratio image ok")

            # check that author md file is present
            if args.authors_folder:
                author_exists = check_author_md(
                    yaml_meta["author"], args.authors_folder
                )
                if not author_exists:
                    msg = "Le fichier de l'auteur/autrice n'a pas pu être trouvé dans le répertoire"
                    logger.error(msg)
                    if args.raise_exceptions:
                        raise ValueError(msg)
                else:
                    logger.info("Markdown de l'auteur/autrice ok")

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
                msg = f"Les tags ne sont pas triés par ordre alphabétique : {yaml_meta['tags']}"
                logger.error(msg)
                if args.raise_exceptions:
                    raise ValueError(msg)
            else:
                logger.info("Ordre alphabétique des tags ok")

            # check that mandatory keys are present
            all_present, missing = check_mandatory_keys(
                yaml_meta.keys(), MANDATORY_KEYS
            )
            if not all_present:
                msg = f"Les clés suivantes ne sont pas présentes dans l'entête markdown : {','.join(missing)}"
                logger.error(msg)
                if args.raise_exceptions:
                    raise ValueError(msg)
            else:
                logger.info("Clés de l'entête ok")