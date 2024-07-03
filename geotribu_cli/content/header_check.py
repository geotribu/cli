import argparse
import logging
import os
from pathlib import Path

import frontmatter
import orjson

from geotribu_cli.constants import (
    GeotribuDefaults,
    YamlHeaderAvailableLicense,
    YamlHeaderMandatoryKeys,
)
from geotribu_cli.json.json_client import JsonFeedClient
from geotribu_cli.utils.check_path import check_path
from geotribu_cli.utils.file_downloader import download_remote_file_to_local
from geotribu_cli.utils.slugger import sluggy

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
        type=Path,
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
        "-maxw",
        "--max-width",
        dest="max_image_width",
        default=800,
        type=int,
        help="Largeur maximum de l'image à vérifier",
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
        "-minr",
        "--min-ratio",
        dest="min_image_ratio",
        default=1.45,
        type=float,
        help="Ratio largeur / hauteur minimum de l'image à vérifier",
    )
    subparser.add_argument(
        "-maxr",
        "--max-ratio",
        dest="max_image_ratio",
        default=1.55,
        type=float,
        help="Ratio largeur / hauteur maximum de l'image à vérifier",
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
    if author == "Geotribu":
        return True
    p = os.path.join(folder, f"{sluggy(author)}.md")
    return os.path.exists(p)


def download_image_sizes() -> dict:
    """Downloads image dimensions file from CDN

    Returns:
            Dict of image dimensions
    """
    # download images sizes and indexes
    local_dims = download_remote_file_to_local(
        remote_url_to_download=f"{defaults_settings.cdn_base_url}img/search-index.json",
        local_file_path=defaults_settings.geotribu_working_folder.joinpath(
            "img/search-index.json"
        ),
        expiration_rotating_hours=24,
    )
    with local_dims.open("rb") as fd:
        img_dims = orjson.loads(fd.read())
        return img_dims["images"]


def check_image_size(
    image_url: str, images: dict, max_width: int, max_height: int
) -> bool:
    """Checks if an image respects provided max dimensions using CDN index file

    Args:
        image_url: HTTP url of the image to check
        images: Dictionary of image dimensions (see download_image_sizes())
        max_width: maximum width of the image
        max_height: maximum height of the image

    Returns:
        True if image max dimensions are respected
        False if not
    """
    key = image_url.replace(f"{defaults_settings.cdn_base_url}img/", "")
    if key not in images:
        return False
    width, height = images[key]
    return width <= max_width and height <= max_height


def check_image_ratio(
    image_url: str, images: dict, min_ratio: int, max_ratio: int
) -> bool:
    key = image_url.replace(f"{defaults_settings.cdn_base_url}img/", "")
    if key not in images:
        return False
    width, height = images[key]
    ratio = width / height
    return min_ratio <= ratio <= max_ratio


def check_image_extension(
    image_url: str,
    allowed_extensions: tuple[str] = defaults_settings.images_header_extensions,
) -> bool:
    ext = image_url.split(".")[-1]
    return ext in allowed_extensions


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
        if sluggy(tags[i].upper()) > sluggy(tags[i + 1].upper()):
            return False
    return True


def check_missing_mandatory_keys(keys: list[str]) -> tuple[bool, set[str]]:
    """Liste les clés de l'en-tête qui sont manquantes par rapport à celles requises.

    Args:
        keys: clés de l'en-tête à comparer

    Returns:
        un tuple à 2 valeurs composé d'un booléen indiquant s'il manque une clé
            obligatoire et la liste des clés manquantes
    """
    missing = set()
    for mandatory_key in YamlHeaderMandatoryKeys.values_set():
        if mandatory_key not in keys:
            missing.add(mandatory_key)
    return len(missing) == 0, missing


def check_license(license_id: str) -> bool:
    """Vérifie que la licence choisie fait partie de celles disponibles.

    Args:
        license: identifiant de la licence.

    Returns:
        True si la licence est l'une de celles disponibles.
    """
    return YamlHeaderAvailableLicense.has_value(license_id)


def run(args: argparse.Namespace) -> None:
    """Run the sub command logic.

    Checks YAML header of a content

    Args:
        args (argparse.Namespace): arguments passed to the subcommand
    """
    logger.debug(f"Running {args.command} with {args}")
    content_paths: list[Path] = args.content_path

    for content_path in content_paths:
        logger.info(f"Checking header of {content_path}")
        check_path(
            input_path=content_path,
            must_be_a_file=True,
            must_be_a_folder=False,
            must_be_readable=True,
            raise_error=True,
        )

        with content_path.open(mode="r", encoding="UTF-8") as file:
            content = frontmatter.load(file)
            yaml_meta = content.metadata
            logger.debug(f"YAML metadata loaded : {yaml_meta}")

            # check that image size is okay
            if "image" in yaml_meta:
                if not yaml_meta["image"]:
                    logger.warning("Pas d'URL pour l'image")
                else:
                    # check image max size
                    if not check_image_size(
                        yaml_meta["image"],
                        download_image_sizes(),
                        args.max_image_width,
                        args.max_image_height,
                    ):
                        msg = (
                            f"Les dimensions de l'image ne sont pas dans l'intervalle autorisé "
                            f"(largeur max: {args.max_image_width},"
                            f"hauteur max: {args.max_image_height})"
                        )
                        logger.error(msg)
                        if args.raise_exceptions:
                            raise ValueError(msg)
                    else:
                        logger.info("Dimensions de l'image ok")

                    # check image max ratio
                    if not check_image_ratio(
                        yaml_meta["image"],
                        download_image_sizes(),
                        args.min_image_ratio,
                        args.max_image_ratio,
                    ):
                        msg = (
                            f"Le ratio largeur / hauteur de l'image n'est pas dans l'intervalle autorisé "
                            f"(min:{args.min_image_ratio},"
                            f"max:{args.max_image_ratio})"
                        )
                        logger.error(msg)
                        if args.raise_exceptions:
                            raise ValueError(msg)
                    else:
                        logger.info("Ratio de l'image ok")

                    # check image extension
                    if not check_image_extension(
                        yaml_meta["image"],
                    ):
                        msg = f"L'extension de l'image n'est pas autorisée, doit être parmi : {','.join(defaults_settings.images_header_extensions)}"
                        logger.error(msg)
                        if args.raise_exceptions:
                            raise ValueError(msg)
                    else:
                        logger.info("Extension de l'image ok")

            # check that author md file is present
            if args.authors_folder:
                for author in yaml_meta["authors"]:
                    author_exists = check_author_md(author, args.authors_folder)
                    if not author_exists:
                        msg = f"Le fichier de l'auteur/autrice '{author}' n'a pas pu être trouvé dans le répertoire"
                        logger.error(msg)
                        if args.raise_exceptions:
                            raise ValueError(msg)
                    else:
                        logger.info(f"Markdown de l'auteur/autrice '{author}' ok")

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
            all_present, missing = check_missing_mandatory_keys(yaml_meta.keys())
            if not all_present:
                msg = f"Les clés suivantes ne sont pas présentes dans l'entête markdown : {','.join(missing)}"
                logger.error(msg)
                if args.raise_exceptions:
                    raise ValueError(msg)
            else:
                logger.info("Clés de l'entête ok")

            # check that license (if present) is in available licenses
            if "license" in yaml_meta:
                license_ok = check_license(yaml_meta["license"])
                if not license_ok:
                    msg = f"La licence ('{yaml_meta['license']}') n'est pas dans celles disponibles ({','.join([l.value for l in YamlHeaderAvailableLicense])})"
                    logger.error(msg)
                    if args.raise_exceptions:
                        raise ValueError(msg)
                else:
                    logger.info("licence ok")
