#! python3  # noqa: E265


# ############################################################################
# ########## IMPORTS #############
# ################################

# standard library
import logging
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import (
    ProxyHandler,
    Request,
    build_opener,
    getproxies,
    install_opener,
    urlopen,
)

# package
from geotribu_cli.__about__ import __title_clean__, __version__
from geotribu_cli.utils.file_stats import is_file_older_than

# ############################################################################
# ########## GLOBALS #############
# ################################

# logs
logger = logging.getLogger(__name__)

# Handle network proxy
proxies_settings = getproxies()  # Get the system proxy settings
proxy_handler = ProxyHandler(proxies_settings)  # Create a proxy handler
opener = build_opener(proxy_handler)  # Create an opener that will use the proxy
install_opener(opener)  # Install the opener

# ############################################################################
# ########## FUNCTIONS ###########
# ################################


def download_remote_file_to_local(
    remote_url_to_download: str,
    local_file_path: Path,
    expiration_rotating_hours: int = 24,
    user_agent: str = f"{__title_clean__}/{__version__}",
    content_type: str = None,
    chunk_size: int = 8192,
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
        chunk_size (int): size of each chunk to read and write in bytes.

    Returns:
        Path: path to the local file (should be the same as local_file_path)
    """
    if local_file_path.exists():
        if is_file_older_than(
            local_file_path=local_file_path,
            expiration_rotating_hours=expiration_rotating_hours,
        ):
            logger.info(
                f"Local search index ({local_file_path}) is outdated: "
                f"updated more than {expiration_rotating_hours} hour(s) ago. "
                "Let's remove and download it again from remote."
            )
            local_file_path.unlink(missing_ok=True)
        else:
            logger.info(
                f"Local search index ({local_file_path}) is up to date. "
                "No download needed.",
            )
            return local_file_path

    # headers
    headers = {"User-Agent": user_agent}
    if content_type:
        headers["Accept"] = content_type

    # download the remote file into local
    custom_request = Request(url=remote_url_to_download, headers=headers)

    try:
        with urlopen(custom_request) as response, local_file_path.open(
            mode="wb"
        ) as buffile:
            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                buffile.write(chunk)
        logger.info(
            f"Le téléchargement du fichier distant {remote_url_to_download} dans "
            f"{local_file_path} a réussi."
        )
    except HTTPError as error:
        logger.error(
            f"Downloading {remote_url_to_download} to {local_file_path} failed. "
            f"Cause: HTTPError. Trace: {error}"
        )
        raise error
    except URLError as error:
        logger.error(
            f"Downloading {remote_url_to_download} to {local_file_path} failed. "
            f"Cause: URLError. Trace: {error}"
        )
        raise error
    except TimeoutError as error:
        logger.error(
            f"Downloading {remote_url_to_download} to {local_file_path} failed. "
            f"Cause: TimeoutError. Trace: {error}"
        )
        raise error
    except Exception as error:
        logger.error(
            f"Downloading {remote_url_to_download} to {local_file_path} failed. "
            f"Cause: Unknown error. Trace: {error}"
        )
        raise error
    return local_file_path
