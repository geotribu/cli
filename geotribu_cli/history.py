#! python3  # noqa: E265

"""Store and load CLI history."""

# ############################################################################
# ########## IMPORTS #############
# ################################

# standard library
import logging
from pathlib import Path
from random import randint

# 3rd party
from rich import print

# package

# ############################################################################
# ########## GLOBALS #############
# ################################

logger = logging.getLogger(__name__)


# ############################################################################
# ########## CLASSES #############
# ################################


class CliHistory:
    """Module to manipulate CLI history."""

    HISTORY_FOLDER_PATH: Path = Path().home() / ".geotribu/history/"

    def __init__(self) -> None:
        """Module instanciation."""
        self.HISTORY_FOLDER_PATH.mkdir(parents=True, exist_ok=True)

    def dump(
        self,
        cmd_name: str,
        results_to_dump: list[dict],
        request_performed: str = "",
        key_field: str = "url",
    ):
        """Dump history.

        Args:
            cmd_name (str): name of the command to save from. Used to customize file name.
            results_to_dump (list[dict]): list of results (dict) to dump
            request_performed (str): operation performed (search term, etc.).
                Defaults to "".
            key_field (str, optional): key in results matching the uri (path, url...).
                Defaults to "url".
        """
        with Path(self.HISTORY_FOLDER_PATH, f"{cmd_name}_latest.history").open(
            mode="w", encoding="UTF-8"
        ) as out_history:
            # request (search, etc.)
            out_history.write(f"{request_performed}\n")

            # results
            for i in results_to_dump:
                out_history.write(f"{i.get(key_field)}\n")

        logger.debug(f"History saved for {cmd_name}")

    def load(self, cmd_name: str = None, result_index: int = -1) -> str:
        """Load from history.

        Args:
            cmd_name (str, optional): load history from specific command. If not
                specified, the latest modified history file is used. Defaults to None.
            result_index (int, optional): result index to return (index 1).
                Defaults to -1. If <0, a random integer is used.

        Returns:
            str: line value from history
        """
        # look for history file to open
        if cmd_name:
            history_file = Path(self.HISTORY_FOLDER_PATH, f"{cmd_name}_latest.history")
        elif history_files := list(self.HISTORY_FOLDER_PATH.glob("*.history")):
            history_file = max(
                history_files,
                key=lambda item: item.stat().st_ctime,
            )
        else:
            print(
                f":person_shrugging: Aucun historique trouvé dans : {self.HISTORY_FOLDER_PATH}"
            )
            return None

        # load history file
        with history_file.open(mode="r", encoding="UTF-8") as in_history:
            # first line is the request
            lines = in_history.readlines()[1:]

        # if no result found, ciao!
        if not len(lines):
            print(f":person_shrugging: Aucun résultat trouvé dans : {history_file}")
            return None

        if result_index <= 0 and len(lines) == 1:
            logger.debug(
                "Index du résultat négatif et liste de résultats égale à 1. "
                "Renvoi du seul résultat."
            )
            return lines[0]
        elif result_index < 0:
            logger.debug(
                "Index du résultat négatif. "
                f"Renvoi d'un index aléatoire parmi les {len(lines)}. "
            )
            return lines[randint(0, len(lines))]
        elif result_index == len(lines):
            return lines[result_index]
        elif result_index > len(lines) and len(lines) >= 2:
            result_index = len(lines) - 2
        elif result_index > len(lines) and len(lines) < 2:
            result_index = -1

        return lines[result_index]
