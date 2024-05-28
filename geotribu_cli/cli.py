#! python3  # noqa: E265

"""Main CLI entrypoint."""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard lib
import argparse
import logging
import sys
from os import getenv

# 3rd party
from rich_argparse import RawDescriptionRichHelpFormatter

# package
from geotribu_cli.__about__ import (
    __author__,
    __cli_usage__,
    __summary__,
    __title__,
    __title_clean__,
    __uri_homepage__,
    __version__,
)
from geotribu_cli.subcommands import (
    parser_comments_broadcast,
    parser_comments_latest,
    parser_comments_read,
    parser_header_check,
    parser_images_optimizer,
    parser_latest_content,
    parser_mastodon_export,
    parser_new_article,
    parser_open_result,
    parser_search_content,
    parser_search_image,
    parser_upgrade,
)
from geotribu_cli.utils.journalizer import configure_logger

# #############################################################################
# ########## Globals ###############
# ##################################

RawDescriptionRichHelpFormatter.usage_markup = True


# ############################################################################
# ########## FUNCTIONS ###########
# ################################


# this serves as a parent parser
def add_common_arguments(parser_to_update: argparse.ArgumentParser):
    """Apply common argument to an existing parser.

    Args:
        parser_to_update (argparse.ArgumentParser): parser to which arguments need to be added

    Returns:
        argparse.ArgumentParser: parser with added options
    """
    parser_to_update.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=1,
        dest="verbosity",
        help="Niveau de verbosité : None = WARNING, -v = INFO, -vv = DEBUG",
    )
    return parser_to_update


def set_default_subparser(
    parser_to_update: argparse.ArgumentParser,
    default_subparser_name: str,
    args: list = None,
):
    """Set a default subparser to a parent parser. Call after setup and just before
        parse_args().
        See: <https://stackoverflow.com/questions/5176691/argparse-how-to-specify-a-default-subcommand>

    Args:
        parser_to_update (argparse.ArgumentParser): parent parser to add
        default_subparser_name (str): name of the subparser to call by default
        args (list, optional): if set is the argument list handed to parse_args().
            Defaults to None.
    """
    subparser_found = False
    for arg in sys.argv[1:]:
        if arg in [
            "-h",
            "--help",
            "--version",
            "--no-logfile",
        ]:  # ignore main parser args
            break

    else:
        for x in parser_to_update._subparsers._actions:
            if not isinstance(x, argparse._SubParsersAction):
                continue
            for sp_name in x._name_parser_map.keys():
                if sp_name in sys.argv[1:]:
                    subparser_found = True
        if not subparser_found:
            # insert default in first position, this implies no
            # global options without a sub_parsers specified
            if args is None:
                sys.argv.insert(1, default_subparser_name)
            else:
                args.insert(0, default_subparser_name)


# ############################################################################
# ########## MAIN ################
# ################################


def main(args: list[str] = None):
    """Main CLI entrypoint.

    Args:
        args (list[str], optional): list of command-line arguments. Defaults to None.
    """
    # create the top-level parser
    main_parser = argparse.ArgumentParser(
        formatter_class=RawDescriptionRichHelpFormatter,
        epilog=f"{__cli_usage__}\n\n"
        f"Développé par {__author__}\n"
        f"Documentation : {__uri_homepage__}",
        description=f"{__title__} {__version__} - {__summary__}",
        argument_default=argparse.SUPPRESS,
        add_help=False,
    )

    # -- ROOT ARGUMENTS --

    # Optional verbosity counter (eg. -v, -vv, -vvv, etc.)
    main_parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=1,
        dest="verbosity",
        help="Niveau de verbosité : None = WARNING, -v = INFO, -vv = DEBUG. Réglable "
        "avec la variable d'environnement GEOTRIBU_LOGS_LEVEL.",
    )

    main_parser.add_argument(
        "--no-logfile",
        default=True,
        action="store_false",
        dest="opt_logfile_disabled",
        help="Désactiver les fichiers de journalisation (logs).",
    )

    main_parser.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="Affiche l'aide et s'arrête là.",
    )

    main_parser.add_argument(
        "--version",
        action="version",
        version=__version__,
        help="Affiche la version du CLI et s'arrête là.",
    )

    # -- SUB-COMMANDS --
    subparsers = main_parser.add_subparsers(title="Sous-commandes", dest="command")

    # Latest Content
    subcmd_latest_content = subparsers.add_parser(
        "read-latest",
        aliases=["récents", "latest", "rl", "rss"],
        help="Consulter les derniers contenus du site",
        formatter_class=main_parser.formatter_class,
        prog="read-latest",
    )
    add_common_arguments(subcmd_latest_content)
    parser_latest_content(subcmd_latest_content)

    # Search Content
    subcmd_search_content = subparsers.add_parser(
        "search-content",
        aliases=["contenus", "sc"],
        help="Rechercher dans les contenus du site",
        formatter_class=main_parser.formatter_class,
        prog="search-content",
    )
    add_common_arguments(subcmd_search_content)
    parser_search_content(subcmd_search_content)

    # Search Image
    subcmd_search_image = subparsers.add_parser(
        "search-image",
        aliases=["si"],
        help="Rechercher dans les images de Geotribu",
        formatter_class=main_parser.formatter_class,
        prog="search-image",
    )
    add_common_arguments(subcmd_search_image)
    parser_search_image(subcmd_search_image)

    # Content reader
    subcmd_opener = subparsers.add_parser(
        "ouvrir",
        aliases=["lire", "open", "or", "read"],
        help="Ouvre un résultat d'une commande précédente dans le terminal ou "
        "l'application correspondant au type de contenu.",
        formatter_class=main_parser.formatter_class,
        prog="open_result",
    )
    add_common_arguments(subcmd_opener)
    parser_open_result(subcmd_opener)

    # Upgrader
    subcmd_upgrade = subparsers.add_parser(
        "upgrade",
        aliases=["auto-update", "maj", "update"],
        help="Mettre à jour Geotribu CLI.",
        formatter_class=main_parser.formatter_class,
        prog="upgrade",
    )
    add_common_arguments(subcmd_upgrade)
    parser_upgrade(subcmd_upgrade)

    subcmd_header_check = subparsers.add_parser(
        "header-check",
        aliases=["header", "check", "header-check", "metadata"],
        help="Vérifier entête markdown",
        formatter_class=main_parser.formatter_class,
        prog="header-check",
    )
    add_common_arguments(subcmd_header_check)
    parser_header_check(subcmd_header_check)

    # -- NESTED SUBPARSER : CREATE ---------------------------------------------------
    subcmd_content_manager = subparsers.add_parser(
        "creer",
        aliases=["new", "nouveau"],
        help="Créer un nouveau contenu.",
        formatter_class=main_parser.formatter_class,
        prog="content_manager",
    )
    content_manager_subparsers = subcmd_content_manager.add_subparsers(
        title="Gestion de contenu", dest="cmd_content_manager"
    )

    # Créer un nouvel article
    subcmd_content_new_article = content_manager_subparsers.add_parser(
        "article",
        help="Créer un nouvel article.",
        formatter_class=main_parser.formatter_class,
        prog="new-article",
    )
    add_common_arguments(subcmd_content_new_article)
    parser_new_article(subcmd_content_new_article)

    # -- NESTED SUBPARSER : COMMENTS ---------------------------------------------------
    subcmd_comments = subparsers.add_parser(
        "comments",
        aliases=["commentaires", "coms"],
        help="Consulter et gérer les commentaires.",
        formatter_class=main_parser.formatter_class,
        prog="comments",
    )
    comments_subparsers = subcmd_comments.add_subparsers(
        title="Commentaires", dest="cmd_comments"
    )

    # Consulter un commentaire
    subcmd_comments_open = comments_subparsers.add_parser(
        "open",
        aliases=["lire", "open", "ouvrir"],
        help="Afficher un commentaire en particulier.",
        formatter_class=main_parser.formatter_class,
        prog="comments-read",
    )
    add_common_arguments(subcmd_comments_open)
    parser_comments_read(subcmd_comments_open)

    # Diffuser un commentaire
    subcmd_comments_broadcast = comments_subparsers.add_parser(
        "broadcast",
        aliases=["diffuser", "publier"],
        help="Diffuser le dernier commentaire sur les réseaux sociaux.",
        formatter_class=main_parser.formatter_class,
        prog="comments-broadcast",
    )
    add_common_arguments(subcmd_comments_broadcast)
    parser_comments_broadcast(subcmd_comments_broadcast)

    # Derniers commentaires
    subcmd_latest_comments = comments_subparsers.add_parser(
        "latest",
        aliases=["derniers", "récents"],
        help="Consulter les derniers commentaires du site",
        formatter_class=main_parser.formatter_class,
        prog="comments-latest",
    )
    add_common_arguments(subcmd_latest_comments)
    parser_comments_latest(subcmd_latest_comments)

    # -- NESTED SUBPARSER : IMAGES ---------------------------------------------------
    subcmd_images = subparsers.add_parser(
        "images",
        aliases=["img"],
        help="Chercher, gérer et optimiser les images.",
        formatter_class=main_parser.formatter_class,
        prog="images",
    )
    images_subparsers = subcmd_images.add_subparsers(title="Images", dest="cmd_images")

    # Optimize Image
    subcmd_image_optimizer = images_subparsers.add_parser(
        "optimize",
        aliases=["process"],
        help="Optimiser une ou plusieurs images pour les téléverser sur le CDN.",
        formatter_class=main_parser.formatter_class,
        prog="optimize-image",
    )
    add_common_arguments(subcmd_image_optimizer)
    parser_images_optimizer(subcmd_image_optimizer)

    # Search Image
    subcmd_search_image = images_subparsers.add_parser(
        "search",
        aliases=["si"],
        help="Rechercher dans les images de Geotribu",
        formatter_class=main_parser.formatter_class,
        prog="search-image",
    )
    add_common_arguments(subcmd_search_image)
    parser_search_image(subcmd_search_image)

    # -- NESTED SUBPARSER : COMMENTS ---------------------------------------------------
    subcmd_social = subparsers.add_parser(
        "social",
        aliases=["rezosocio", "social"],
        help="Commandes liées aux réseaux sociaux.",
        formatter_class=main_parser.formatter_class,
        prog="social",
    )
    social_subparsers = subcmd_social.add_subparsers(title="Social", dest="cmd_social")

    # Mastodon - Export
    subcmd_social_matsodon_export = social_subparsers.add_parser(
        "mastodon-export",
        help="Exporter les données du compte Mastodon (listes, comptes suivis...).",
        formatter_class=main_parser.formatter_class,
        prog="mastodon-export",
    )
    add_common_arguments(subcmd_social_matsodon_export)
    parser_mastodon_export(subcmd_social_matsodon_export)

    # -- PARSE ARGS --------------------------------------------------------------------
    set_default_subparser(
        parser_to_update=main_parser,
        default_subparser_name=getenv("GEOTRIBU_DEFAULT_SUBCOMMAND", "read-latest"),
    )

    # just get passed args
    args = main_parser.parse_args(args)

    # log configuration
    if args.opt_logfile_disabled:
        configure_logger(
            verbosity=args.verbosity, logfile=f"{__title_clean__}_{__version__}.log"
        )
    else:
        configure_logger(verbosity=args.verbosity)

    # add the handler to the root logger
    logger = logging.getLogger(__title_clean__)
    logger.debug(f"Log level set: {logging.getLevelName(args.verbosity)}")

    # -- RUN LOGIC --
    if hasattr(args, "func"):
        args.func(args)


# -- Stand alone execution
if __name__ == "__main__":
    main()  # required by unittest
