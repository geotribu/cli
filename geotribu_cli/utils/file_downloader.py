#! python3  # noqa: E265


# ############################################################################
# ########## IMPORTS #############
# ################################

# standard library
import logging
from datetime import datetime, timedelta
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# package
from geotribu_cli.__about__ import __title_clean__, __version__

# ############################################################################
# ########## GLOBALS #############
# ################################

# logs
logger = logging.getLogger(__name__)

# ############################################################################
# ########## FUNCTIONS ###########
# ################################


def download_remote_file_to_local(
    url_index_to_download: str,
    local_file_path: Path,
    expiration_rotating_hours: int = 24,
    user_agent: str = f"{__title_clean__}/{__version__}",
) -> Path:
    """Check if the local index file exists. If not, download the search index from \
        remote URL. If it does exist, check if it has been modified.

    Args:
        url_index_to_download (str): remote URL of the search index
        local_file_path (Path): local path to the index file
        expiration_rotating_hours (int, optional): number in hours to consider the local file outaded. Defaults to 24.
        user_agent (str, optional): user agent to use to perform the request. Defaults to f"{__title_clean__}/{__version__}".

    Returns:
        Path: path to the local index file (should be the same as local_file_path)
    """
    # content search index
    if local_file_path.exists():
        f_creation = datetime.fromtimestamp(local_file_path.stat().st_ctime)
        if (datetime.now() - f_creation) < timedelta(hours=expiration_rotating_hours):
            logger.info(
                f"Local search index ({local_file_path}) is up to date. "
                "No download needed.",
            )
            return local_file_path
        else:
            logger.info(
                f"Local search index ({local_file_path}) is outdated: "
                f"updated more than {expiration_rotating_hours} hour(s) ago. "
                "Let's remove and download it again from remote."
            )
            local_file_path.unlink(missing_ok=True)

    # download the remote file into local
    custom_request = Request(
        url=url_index_to_download,
        headers={"User-Agent": user_agent, "Accept": "application/json"},
    )

    try:
        with urlopen(custom_request) as response:
            with local_file_path.open(mode="wb") as tmp_file:
                tmp_file.write(response.read())
        logger.info(
            f"Téléchargement du fichier distant {url_index_to_download} dans {local_file_path} a réussi."
        )
    except HTTPError as error:
        logger.error(error)
        return error
    except URLError as error:
        logger.error(error)
        return error
    except TimeoutError as error:
        logger.error(error)
        return error

    return local_file_path
