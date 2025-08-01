#! python3  # noqa: E265

"""
Launch PyInstaller using a Python script.
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import platform
import sys
from os import getenv
from pathlib import Path

# 3rd party
import PyInstaller.__main__

# package
sys.path.insert(0, str(Path(".").resolve()))
from geotribu_cli import __about__  # noqa: E402

# #############################################################################
# ########### MAIN #################
# ##################################
package_folder = Path("geotribu_cli")

mac_os_version, _, _ = platform.mac_ver()
mac_os_version = "-".join(mac_os_version.split(".")[:2])

PyInstaller.__main__.run(
    [
        "--log-level={}".format(getenv("PYINSTALLER_LOG_LEVEL", "WARN")),
        "--name={}_{}_MacOS{}".format(
            __about__.__title_clean__,
            __about__.__version__.replace(".", "-"),
            mac_os_version,
        ),
        "--noconfirm",
        "--noupx",
        "--onefile",
        "--console",
        str(package_folder / "cli.py"),
    ]
)
