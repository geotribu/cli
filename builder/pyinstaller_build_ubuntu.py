#! python3  # noqa: E265

"""
Launch PyInstaller using a Python script.
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import sys
from os import getenv
from pathlib import Path

# 3rd party
import distro
import PyInstaller.__main__

# package
sys.path.insert(0, str(Path(".").resolve()))
from geotribu_cli import __about__  # noqa: E402

# #############################################################################
# ########### MAIN #################
# ##################################
package_folder = Path("geotribu_cli")

PyInstaller.__main__.run(
    [
        "--log-level={}".format(getenv("PYINSTALLER_LOG_LEVEL", "WARN")),
        "--name={}_{}_{}{}.bin".format(
            __about__.__title_clean__,
            __about__.__version__.replace(".", "-"),
            distro.name(),
            distro.version(),
        ),
        "--noconfirm",
        "--noupx",
        "--onefile",
        "--console",
        str(package_folder / "cli.py"),
    ]
)
