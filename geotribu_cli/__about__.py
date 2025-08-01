#! python3  # noqa: E265

"""
Metadata bout the package to easily retrieve informations about it.
See: https://packaging.python.org/guides/single-sourcing-package-version/
"""

from datetime import date

__all__ = [
    "__author__",
    "__copyright__",
    "__email__",
    "__license__",
    "__summary__",
    "__title__",
    "__uri__",
    "__version__",
]

__author__ = "Julien Moura (Geotribu)"
__copyright__ = f"2022 - {date.today().year}, {__author__}"
__email__ = "geotribu@gmail.com"
__executable_name__ = "geotribu"
__keywords__ = ["cli", "Geotribu", "GIS"]
__license__ = "MIT"
__package_name__ = "geotribu"
__summary__ = (
    "Une ligne de commande pour Geotribu qui offre des outils pour rechercher "
    "et consulter les contenus et images, et faciliter les tâches récurrentes des "
    "contributeur/ices."
)
__title__ = "Geotribu Toolbelt"
__title_clean__ = "".join(e for e in __title__ if e.isalnum())
__uri_homepage__ = "https://cli.geotribu.fr/"
__uri_repository__ = "https://github.com/geotribu/cli/"
__uri_tracker__ = f"{__uri_repository__}issues/"

__uri__ = __uri_repository__

__version__ = "0.34.3"
__version_info__ = tuple(
    [
        int(num) if num.isdigit() else num
        for num in __version__.replace("-", ".", 1).split(".")
    ]
)

__cli_usage__ = (
    "Geotribu en ligne de commande pour rechercher dans les contenus et les images, "
    "consulter les derniers contenus sans quitter son terminal.\n"
    "Encore meilleur avec les terminaux gérant les hyperliens : Bash, PowerShell 5+, etc."
)
