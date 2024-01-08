#! python3  # noqa: E265


# ############################################################################
# ########## IMPORTS #############
# ################################

# standard library
import logging
from pathlib import Path
from typing import Optional
from urllib.error import HTTPError

# 3rd party
from requests import Session
from requests.exceptions import ConnectionError, HTTPError
from requests.utils import requote_uri

# package
from geotribu_cli.__about__ import __title_clean__, __version__
from geotribu_cli.utils.file_stats import is_file_older_than
from geotribu_cli.utils.proxies import get_proxy_settings

# ############################################################################
# ########## GLOBALS #############
# ################################

# logs
logger = logging.getLogger(__name__)

# ############################################################################
# ########## FUNCTIONS ###########
# ################################


def download_remote_file_to_local(
    remote_url_to_download: str,
    local_file_path: Path,
    expiration_rotating_hours: int = 24,
    user_agent: str = f"{__title_clean__}/{__version__}",
    content_type: Optional[str] = None,
    chunk_size: int = 8192,
    timeout=(800, 800),
) -> Path:
    """Check if the local index file exists. If not, download the search index from \
        remote URL. If it does exist, check if it has been modified.

    Args:
        remote_url_to_download (str): remote URL of the file to download
        local_file_path (Path): local path to the file
        expiration_rotating_hours (int, optional): number in hours to consider the \
            local file outdated. Defaults to 24.
        user_agent (str, optional): user agent to use to perform the request. Defaults \
            to f"{__title_clean__}/{__version__}".
        content_type (str): HTTP content-type.
        chunk_size (int): size of each chunk to read and write in bytes. Defaults to \
            8192.
        timeout (tuple, optional): custom timeout (request, response). Defaults to \
            (800, 800).

    Returns:
        Path: path to the local file (should be the same as local_file_path)
    """
    if local_file_path.exists():
        if is_file_older_than(
            local_file_path=local_file_path,
            expiration_rotating_hours=expiration_rotating_hours,
        ):
            logger.info(
                f"Le fichier local ({local_file_path}) est périmé: "
                f"il a été mis à jour il y a plus de {expiration_rotating_hours} heures."
                "Il a besoin d'être de nouveau téléchargé."
            )
            local_file_path.unlink(missing_ok=True)
        else:
            logger.info(
                f"Le fichier local ({local_file_path}) est à jour par rapport au délai "
                f"d'expiration spécifié ({expiration_rotating_hours}). Pas besoin de le retélécharger.",
            )
            return local_file_path

    # make sure parents folder exist
    local_file_path.parent.mkdir(parents=True, exist_ok=True)

    # headers
    headers = {"User-Agent": user_agent}
    if content_type:
        headers["Accept"] = content_type

    try:
        with Session() as dl_session:
            dl_session.proxies.update(get_proxy_settings())
            dl_session.headers.update(headers)

            with dl_session.get(
                url=requote_uri(remote_url_to_download), stream=True, timeout=timeout
            ) as req:
                req.raise_for_status()

                with local_file_path.open(mode="wb") as buffile:
                    for chunk in req.iter_content(chunk_size=chunk_size):
                        if chunk:
                            buffile.write(chunk)
            logger.info(
                f"Le téléchargement du fichier distant {remote_url_to_download} dans "
                f"{remote_url_to_download} a réussi. "
            )
    except HTTPError as error:
        logger.error(
            f"Downloading {remote_url_to_download} to {local_file_path} failed. "
            f"Cause: HTTPError. Trace: {error}"
        )
        raise error
    except ConnectionError as error:
        logger.error(
            f"Downloading {remote_url_to_download} to {local_file_path} failed. "
            f"Cause: ConnectionError. Trace: {error}"
        )
        raise error
    except Exception as error:
        logger.error(
            f"Downloading {remote_url_to_download} to {local_file_path} failed. "
            f"Cause: Unknown error. Trace: {error}"
        )
        raise error

    return local_file_path
