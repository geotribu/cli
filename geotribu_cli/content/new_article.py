#! python3  # noqa: E265

# ############################################################################
# ########## IMPORTS #############
# ################################

# standard library
import argparse
import logging
from datetime import datetime, timedelta

import frontmatter

# package
from geotribu_cli.constants import GeotribuDefaults
from geotribu_cli.utils.file_downloader import download_remote_file_to_local

# 3rd party


# ############################################################################
# ########## GLOBALS #############
# ################################

logger = logging.getLogger(__name__)
defaults_settings = GeotribuDefaults()


# ############################################################################
# ########## FUNCTIONS ###########
# ################################


# ############################################################################
# ########## CLI #################
# ################################


def parser_new_article(
    subparser: argparse.ArgumentParser,
) -> argparse.ArgumentParser:
    """Set the argument parser for subcommand.

    Args:
        subparser (argparse.ArgumentParser): parser to set up

    Returns:
        argparse.ArgumentParser: parser ready to use
    """
    subparser.add_argument(
        "-t",
        "--title",
        "--titre",
        default=None,
        dest="titre",
        help="Titre de l'article. Si vide, il sera de la forme 'Projet d'article'",
    )

    subparser.add_argument(
        "-d",
        "--date",
        default=None,
        dest="publication_date",
        type=str,
        help="Date de publication envisagée au format AAAA-MM-JJ. Exemple : "
        f"{datetime.today():%Y-%m-%d}. Si vide, 2 semaines à compter de la date du jour.",
    )

    subparser.set_defaults(func=run)

    return subparser


# ############################################################################
# ########## MAIN ################
# ################################


def run(args: argparse.Namespace):
    """Run the sub command logic.

    Download the RSS feed file and display results.

    Args:
        args (argparse.Namespace): arguments passed to the subcommand
    """
    logger.debug(f"Running {args.command} with {args}")

    # download or load the article template
    article_tpl_local = download_remote_file_to_local(
        remote_url_to_download=f"{defaults_settings.site_git_source_base_url(mode='raw')}"
        f"{defaults_settings.template_article}",
        local_file_path=defaults_settings.geotribu_working_folder.joinpath(
            "templates/article.md"
        ),
        expiration_rotating_hours=24 * 30,
        content_type="text/plain; charset=utf-8",
    )

    # if no date specified, use 3 weeks later
    if args.publication_date is None:
        today_2w = datetime.today() + timedelta(weeks=3)
        args.publication_date = f"{today_2w:%Y-%m-%d}"

    # load template
    with article_tpl_local.open(encoding="UTF-8") as f:
        article = frontmatter.load(f)

    # replace with values
    article.metadata["date"] = f"{args.publication_date} 10:20"

    # write output
    out_filepath = defaults_settings.geotribu_working_folder.joinpath(
        f"drafts/{args.publication_date}_titre.md"
    )
    out_filepath.parent.mkdir(parents=True, exist_ok=True)
    with out_filepath.open(mode="w", encoding="UTF-8") as out_file:
        out_file.write(frontmatter.dumps(article))


# -- Stand alone execution
if __name__ == "__main__":
    pass
