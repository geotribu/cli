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

PyInstaller.__main__.run(
    [
        "--add-data=LICENSE;.",
        "--add-data=README.md;.",
        "--clean",
        "--icon={}".format(
            Path(__file__).parent.joinpath("frozen_app_icon.ico").resolve()
        ),
        "--log-level={}".format(getenv("PYINSTALLER_LOG_LEVEL", "WARN")),
        "--manifest={}".format((package_folder / "../builder/manifest.xml").resolve()),
        f"--name={__about__.__title_clean__}_{__about__.__version__.replace('.', '-')}_"
        f"{platform.system()}{platform.architecture()[0]}",
        "--noconfirm",
        "--noupx",
        "--onefile",
        "--version-file={}".format("version_info.txt"),
        str(package_folder / "cli.py"),
    ]
)
