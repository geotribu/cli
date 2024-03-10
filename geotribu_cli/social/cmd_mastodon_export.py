#! python3  # noqa: E265

# ############################################################################
# ########## IMPORTS #############
# ################################

# standard library
import argparse
import logging
from os import getenv
from pathlib import Path

# package
from geotribu_cli.constants import GeotribuDefaults
from geotribu_cli.social.mastodon_client import ExtendedMastodonClient

# ############################################################################
# ########## GLOBALS #############
# ################################

logger = logging.getLogger(__name__)
defaults_settings = GeotribuDefaults()


# ############################################################################
# ########## CLI #################
# ################################


def parser_mastodon_export(
    subparser: argparse.ArgumentParser,
) -> argparse.ArgumentParser:
    """Set the argument parser for subcommand.

    Args:
        subparser (argparse.ArgumentParser): parser to set up

    Returns:
        argparse.ArgumentParser: parser ready to use
    """

    subparser.add_argument(
        "-w",
        "--where",
        help="Dossier dans lequel exporter les fichiers.",
        default=getenv(
            "GEOTRIBU_MASTODON_EXPORT_DEST_FOLDER",
            defaults_settings.geotribu_working_folder.joinpath("mastodon/"),
        ),
        type=Path,
        dest="dest_export_folder",
    )

    subparser.set_defaults(func=run)

    return subparser


# ############################################################################
# ########## MAIN ################
# ################################


def run(args: argparse.Namespace):
    """Run the sub command logic.

    Open result of a previous command.

    Args:
        args (argparse.Namespace): arguments passed to the subcommand
    """
    logger.debug(f"Running {args.command} with {args}")

    mastodon_client = ExtendedMastodonClient()
    mastodon_client.export_data(
        dest_path_following_accounts=Path(args.dest_export_folder).joinpath(
            "mastodon_comptes_suivis_geotribu.csv"
        ),
        dest_path_lists=Path(args.dest_export_folder).joinpath(
            "mastodon_listes_geotribu.csv"
        ),
        dest_path_lists_only_accounts=Path(args.dest_export_folder).joinpath(
            "mastodon_comptes_des_listes_geotribu.csv"
        ),
    )
