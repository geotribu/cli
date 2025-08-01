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
from os import getenv
from pathlib import Path
from sys import platform as opersys
from urllib.parse import urlsplit, urlunsplit
from urllib.request import Request, urlopen

# 3rd party library
from packaging.version import Version
from rich.markdown import Markdown

# submodules
from geotribu_cli.__about__ import (
    __package_name__,
    __title__,
    __title_clean__,
    __uri_repository__,
)
from geotribu_cli.__about__ import __version__ as actual_version
from geotribu_cli.console import console
from geotribu_cli.constants import GeotribuDefaults
from geotribu_cli.utils.file_downloader import download_remote_file_to_local
from geotribu_cli.utils.str2bool import str2bool

# #############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)
defaults_settings = GeotribuDefaults()

# #############################################################################
# ####### Functions ###############
# #################################


def get_download_url_for_os(
    release_assets: list, override_opersys: str = None
) -> tuple[str, str]:
    """Parse list of a GitHub release assets and return the appropriate download URL \
        for the current operating system.

    Args:
        release_assets (list): list of assets
        override_opersys (str, optional): override current operating system code. Useful
            to get a download URL for a specific OS. Defaults to None.

    Returns:
        tuple[str, str]: tuple containing asset download URL (browser_download_url) and
            content-type (barely defined)
    """
    opersys_code = opersys
    if override_opersys is not None:
        opersys_code = override_opersys

    for asset in release_assets:
        if opersys_code == "win32" and "Windows" in asset.get("name"):
            return asset.get("browser_download_url"), asset.get("content-type")
        elif opersys_code == "linux" and "Ubuntu" in asset.get("name"):
            return asset.get("browser_download_url"), asset.get("content-type")
        elif opersys_code == "darwin" and "MacOS" in asset.get("name"):
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

    # headers
    headers = {
        "content-type": "application/vnd.github+json",
        "User-Agent": f"{__title_clean__}/{actual_version}",
    }

    if getenv("GITHUB_TOKEN"):
        logger.debug(
            f"Using authenticated request to GH API: {getenv('GITHUB_TOKEN')[:9]}****"
        )
        headers["Authorization"] = f"Bearer {getenv('GITHUB_TOKEN')}"

    request = Request(url=request_url, headers=headers)

    try:
        with urlopen(request) as response:
            if response.status == 200:
                release_info = json.loads(response.read())
        return release_info
    except Exception as err:
        logger.error(err)
        if "rate limit exceeded" in err:
            logger.error(
                "Rate limit of GitHub API exeeded. Try again later (generally "
                "in 15 minutes) or set GITHUB_TOKEN as environment variable with a "
                "personal token."
            )
        return None


def replace_domain(url: str, new_domain: str = "api.github.com/repos") -> str:
    """Replaces the domain of an URL with a new domain.

    Args:
        url (str): The original URL.
        new_domain (str, optional): The new domain to replace the original domain with.
            Defaults to "api.github.com/repos".

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
        help="Vérifie seulement la disponibilité d'une nouvelle version, sans télécharger.",
        default=str2bool(getenv("GEOTRIBU_UPGRADE_CHECK_ONLY", False)),
        action="store_true",
        dest="opt_only_check",
    )

    subparser.add_argument(
        "-n",
        "--dont-show-release-notes",
        help="Display release notes.",
        default=str2bool(getenv("GEOTRIBU_UPGRADE_DISPLAY_RELEASE_NOTES", True)),
        action="store_false",
        dest="opt_show_release_notes",
    )

    subparser.add_argument(
        "-w",
        "--where",
        help="Dossier dans lequel télécharger la nouvelle version.",
        default=getenv("GEOTRIBU_UPGRADE_DOWNLOAD_FOLDER", "./"),
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
    if Version(actual_version) < Version(latest_version):
        console.print(f"Une nouvelle version est disponible : {latest_version}")
        if args.opt_show_release_notes:
            version_change = Markdown(latest_release.get("body"))
            console.print(version_change)
            print("\n")
        if args.opt_only_check:
            sys.exit(0)
    else:
        console.print(
            f"Vous disposez déjà de la dernière version publiée : {latest_version}"
        )
        sys.exit(0)

    # -- DOWNLOAD ------------------------------------------------------------

    # check if we are in frozen mode (typically PyInstaller) or as "normal" Python
    if not (getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")):
        logger.debug("Running in a normal Python process.")
        console.print(
            "\n\n:snake: Pour mettre à jour (adapter selon votre environnement) :"
            f"\n\n[code]python -m pip install -U {__package_name__}[/code]"
        )
        sys.exit(0)

    # select remote download URL
    if release_asset_for_os := get_download_url_for_os(latest_release.get("assets")):
        remote_url, remote_content_type = release_asset_for_os
    else:
        sys.exit(
            "Impossible de déterminée une URL de téléchargement adéquate pour "
            f"le système {opersys}."
        )

    # handle empty content-type
    if remote_content_type is None:
        remote_content_type = "application/octet-stream"

    # destination local file
    dest_filepath = Path(
        args.local_download_folder, Path(urlsplit(remote_url).path).name
    )

    # download it
    logger.info = (
        f"Téléchargement de la nouvelle version '{latest_version}' depuis "
        f"{remote_url} vers {dest_filepath}"
    )

    with console.status("Téléchargement de la nouvelle version...", spinner="earth"):
        try:
            download_remote_file_to_local(
                remote_url_to_download=remote_url,
                local_file_path=dest_filepath,
                content_type=remote_content_type,
            )
        except Exception as err:
            sys.exit(f"Le téléchargement de la dernière version a échoué. Trace: {err}")

    console.print(f"Nouvelle version de {__title__} téléchargée ici : {dest_filepath}.")


# #############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """Standalone execution."""
    pass
