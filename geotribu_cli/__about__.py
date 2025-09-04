#! python3  # noqa: E265

"""Abstraction on the package metadata to easily retrieve them."""


from datetime import date
from importlib import metadata

_pkg_metadata = metadata.metadata("geotribu") or {}

try:
    from ._version import version as __version__
except ImportError:
    __version__ = _pkg_metadata.get("Version", "0.0.0-dev0")


__author__: str = _pkg_metadata.get("Author", "Julien Moura (Geotribu)")
__copyright__: str = f"2022 - {date.today().year}, {__author__}"
__email__: str = "geotribu@gmail.com"
__executable_name__: str = "geotribu"
__keywords__: list[str] = _pkg_metadata.get("Keywords", "cli,Geotribu,GIS").split(",")
__license__: str = _pkg_metadata.get("License-Expression", "MIT")
__package_name__ = _pkg_metadata.get("Name", "geotribu")
__summary__ = _pkg_metadata.get(
    "Summary",
    "Une ligne de commande pour Geotribu qui offre des outils pour rechercher "
    "et consulter les contenus et images, et faciliter les tâches récurrentes des "
    "contributeur/ices.",
)
__title__: str = "Geotribu Toolbelt"
__title_clean__: str = "".join(e for e in __title__ if e.isalnum())
__uri_homepage__: str = "https://cli.geotribu.fr/"
__uri_repository__: str = "https://github.com/geotribu/cli/"
__uri_tracker__: str = f"{__uri_repository__}issues/"

__uri__ = __uri_repository__
__version_info__: tuple[int, int, int, str | None, str | None] = tuple(
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
