#! python3  # noqa: E265

"""
    Sub-command in charge of checking if new versions are available.

    Author: Julien M. (https://github.com/guts)
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import argparse
import json
import logging
import sys
from pathlib import Path
from sys import platform as opersys
from urllib.parse import urlsplit, urlunsplit
from urllib.request import urlopen

# 3rd party library
import semver
from rich import print

# submodules
from geotribu_cli.__about__ import __title__, __uri_repository__
from geotribu_cli.__about__ import __version__ as actual_version
from geotribu_cli.constants import GeotribuDefaults
from geotribu_cli.utils.file_downloader import download_remote_file_to_local

# #############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)
defaults_settings = GeotribuDefaults()

# #############################################################################
# ####### Functions ###############
# #################################


def get_download_url_for_os(release_assets: list) -> str:
    """Parse list of a GitHub release assets and return the appropriate download URL \
        for the current operating system.

    Args:
        release_assets (list): list of assets

    Returns:
        str: asset download URL (browser_download_url)
    """
    for asset in release_assets:
        if opersys == "win32" and "Windows" in asset.get("name"):
            return asset.get("browser_download_url"), asset.get("content-type")
        elif opersys == "linux" and "Ubuntu" in asset.get("name"):
            return asset.get("browser_download_url"), asset.get("content-type")
        elif opersys == "darwin" and "MacOS" in asset.get("name"):
            return asset.get("browser_download_url"), asset.get("content-type")
        else:
            continue

    return None


def get_latest_release(api_repo_url: str) -> dict:
    """Get latest release from GitHub public API.

    Args:
        api_repo_url (str): API URL with the owner and repository set

    Returns:
        dict: GitHub release object
    """

    request_url = f"{api_repo_url}releases/latest"
    try:
        response = urlopen(request_url)
        if response.status == 200:
            release_info = json.loads(response.read())
            return release_info
    except Exception as err:
        logger.error(err)
        return None


def replace_domain(url: str, new_domain: str) -> str:
    """
    Replaces the domain of an URL with a new domain.

    Args:
        url (str): The original URL.
        new_domain (str): The new domain to replace the original domain with.

    Returns:
        str: The URL with the new domain.
    """
    split_url = urlsplit(url)
    split_url = split_url._replace(netloc=new_domain)
    new_url = urlunsplit(split_url)
    return new_url


# ############################################################################
# ########## CLI #################
# ################################


def parser_upgrade(
    subparser: argparse.ArgumentParser,
) -> argparse.ArgumentParser:
    """Set the argument parser subcommand.

    Args:
        subparser (argparse.ArgumentParser): parser to set up

    Returns:
        argparse.ArgumentParser: parser ready to use
    """
    subparser.add_argument(
        "-c",
        "--check-only",
        help="Vérifie seulement la disponibilité d'une nouvelle version.",
        default=False,
        action="store_true",
        dest="opt_only_check",
    )

    subparser.add_argument(
        "-w",
        "--where",
        help="Dossier dans lequel télécharger la nouvelle version.",
        default="./",
        type=Path,
        dest="local_download_folder",
    )

    subparser.set_defaults(func=run)

    return subparser


# ############################################################################
# ########## MAIN ################
# ################################


def run(args: argparse.Namespace):
    """Run the sub command logic.

    Check if a new version of the CLI is available and download it if needed.

    Args:
        args (argparse.Namespace): arguments passed to the subcommand
    """
    logger.debug(f"Running {args.command} with {args}")

    # build API URL from repository
    api_url = replace_domain(url=__uri_repository__, new_domain="api.github.com/repos")

    # get latest release as dictionary
    latest_release = get_latest_release(api_repo_url=api_url)

    if not latest_release:
        sys.exit(f"Impossible de récupérer la dernière release depuis {api_url}.")

    # compare it
    latest_version = latest_release.get("tag_name")
    if semver.VersionInfo.parse(actual_version) < semver.VersionInfo.parse(
        latest_version
    ):
        print(f"Une nouvelle version est disponible : {latest_version}")
        if args.opt_only_check:
            sys.exit(0)
    else:
        print(f"Vous disposez déjà de la dernière version publiée : {latest_version}")
        sys.exit(0)

    # -- DOWNLOAD ------------------------------------------------------------

    # select remote download URL
    remote_url, remote_content_type = get_download_url_for_os(
        latest_release.get("assets")
    )
    if not remote_url:
        sys.exit(
            "Impossible de déterminée une URL de téléchargement adéquate pour "
            f"le système {opersys}."
        )

    # destination local file
    dest_filepath = Path(
        args.local_download_folder, Path(urlsplit(remote_url).path).name
    )

    # download it
    logger.info(
        f"Téléchargement de la nouvelle version '{latest_version}' depuis {remote_url} "
        f"vers {dest_filepath}"
    )
    try:
        download_remote_file_to_local(
            remote_url_to_download=remote_url,
            local_file_path=dest_filepath,
            content_type=remote_content_type,
        )
    except Exception as err:
        sys.exit(f"Le téléchargement de la dernière version a échoué. Trace: {err}")

    print(f"Nouvelle version de {__title__} téléchargée ici : {dest_filepath}.")


# #############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """Standalone execution."""
    pass
