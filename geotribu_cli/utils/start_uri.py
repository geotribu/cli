"""Cross-platform helper to open a file with the default operating system application."""

# standard library
import subprocess
import webbrowser
from pathlib import Path
from sys import platform as opersys
from typing import Union

# imports depending on operating system
if opersys == "win32":
    from os import startfile

# package
from geotribu_cli.utils.check_path import check_path


def open_uri(in_filepath: Union[str, Path]):
    """Open a file or a directory in the explorer or URL in the web browser of the
        operating system.

    Args:
        in_filepath (Union[str, Path]): path to the file/folder or url to open.
    """

    if "://" in str(in_filepath):
        url = in_filepath
        return webbrowser.open(url)

    # check if the file or the directory exists
    check_path(
        input_path=in_filepath,
        must_exists=True,
        must_be_readable=True,
        must_be_a_file=False,
        must_be_a_folder=True,
    )

    # open the directory or the file according to the os
    if opersys == "win32":  # Windows
        proc = startfile(in_filepath)

    elif opersys.startswith("linux"):  # Linux:
        proc = subprocess.Popen(
            ["xdg-open", in_filepath], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

    elif opersys == "darwin":  # Mac:
        proc = subprocess.Popen(
            ["open", "--", in_filepath], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

    else:
        raise NotImplementedError(
            "Your `%s` isn't a supported operating system`." % opersys
        )

    # end of function
    return proc
