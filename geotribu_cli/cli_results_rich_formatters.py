#! python3  # noqa: E265

# ############################################################################
# ########## IMPORTS #############
# ################################

# standard library
import logging
from functools import lru_cache
from typing import Optional, Union

# 3rd party
from rich.table import Table

# package
from geotribu_cli.__about__ import __title__, __version__
from geotribu_cli.comments.mdl_comment import Comment
from geotribu_cli.constants import GeotribuDefaults
from geotribu_cli.utils.formatters import url_add_utm

# ############################################################################
# ########## GLOBALS #############
# ################################

logger = logging.getLogger(__name__)
defaults_settings = GeotribuDefaults()


# ############################################################################
# ########## FUNCTIONS ###########
# ################################


def format_output_result_comments(
    results: list[Comment], format_type: Optional[str] = None, count: int = 5
) -> Union[Table, list[Comment]]:
    """Format list of comments according to output option.

    Args:
        results: result to format
        format_type: format output option. Defaults to None.
        count: default number of results to display. Defaults to 5.

    Returns:
        formatted result ready to print, table or inital list
    """
    if format_type == "table":
        table = Table(
            title=f"Derniers commentaires publiés - {count}/{len(results)} résultats "
            f"\n(ctrl+clic sur le numéro pour ouvrir dans le navigateur)",
            show_lines=True,
            highlight=True,
            caption=f"{__title__} {__version__}",
        )

        # columns
        table.add_column(header="#", justify="center")
        table.add_column(header="Date", justify="center")
        table.add_column(header="Auteur/e", justify="left", style="default")
        table.add_column(header="Contenu", justify="center", style="magenta")
        table.add_column(header="Réponse à", justify="center")
        table.add_column(header="Commentaire", justify="center")

        # iterate over results

        for r in results[:count]:
            # add row
            table.add_row(
                f"[link={r.url_to_comment}]{r.id}[/link]",
                f"{r.created_as_datetime:%d %B %Y \nà %H:%m}",
                r.author,
                f"[link={r.url_to_comment}]{r.uri}[/link]",
                str(r.parent),
                r.markdownified_text,
            )

        return table
    else:
        return results


def format_output_result_search_content(
    result: list[dict],
    search_term: Optional[str] = None,
    format_type: Optional[str] = None,
    count: int = 5,
    search_filter_dates: Optional[tuple] = None,
    search_filter_type: Optional[str] = None,
) -> Union[list[dict], Table]:
    """Format result according to output option.

    Args:
        result (list[dict]): result to format
        search_term (str, optional): term used for search. Defaults to None.
        format_type (str, optional): format output option. Defaults to None.
        count (int, optional): default number of results to display. Defaults to 5.
        search_filter_dates: dates used to filter search. Defaults to None.
        search_filter_type: type used to filter search. Defaults to None.

    Returns:
        str: formatted result ready to print
    """
    if format_type == "table":
        # formatte le titre - plus lisible qu'une grosse f-string des familles
        titre = add_search_criteria_as_str(
            in_txt="Recherche de contenus",
            search_filter_dates=search_filter_dates,
            search_filter_type=search_filter_type,
            search_term=search_term,
            search_results_total=len(result),
            search_results_displayed=count,
            hint="Astuce : ctrl+clic sur le titre pour ouvrir le contenu",
        )

        table = Table(
            title=titre,
            show_lines=True,
            highlight=True,
            caption=f"{__title__} {__version__}",
        )

        # columns
        table.add_column(header="#", justify="center")
        table.add_column(header="Titre", justify="left", style="default")
        table.add_column(header="Type", justify="center", style="bright_black")
        table.add_column(
            header="Date de publication", justify="center", style="bright_black"
        )
        table.add_column(header="Score", style="magenta")
        table.add_column(header="Mots-clés", justify="right", style="blue")

        # iterate over results
        for r in result[:count]:
            table.add_row(
                f"{result.index(r)}",
                f"[link={url_add_utm(r.get('url'))}]{r.get('titre')}[/link]",
                r.get("type"),
                f"{r.get('date'):%d %B %Y}",
                r.get("score"),
                ",".join(r.get("tags")),
            )

        return table
    else:
        return result[:count]


def format_output_result_search_image(
    result: list[dict],
    search_term: Optional[str] = None,
    format_type: Optional[str] = None,
    count: int = 5,
    search_filter_type: Optional[str] = None,
) -> Union[list[dict], Table]:
    """Format result according to output option.

    Args:
        result (list[dict]): result to format
        search_term (str, optional): term used for search. Defaults to None.
        format_type (str, optional): format output option. Defaults to None.
        count (int, optional): default number of results to display. Defaults to 5.

    Returns:
        str: formatted result ready to print
    """
    if format_type == "table":
        titre = add_search_criteria_as_str(
            in_txt="Recherche dans les images",
            search_term=search_term,
            search_filter_type=search_filter_type,
            search_results_total=len(result),
            search_results_displayed=count,
            hint="Astuce : ctrl+clic sur le nom pour ouvrir l'image",
        )

        table = Table(
            title=titre,
            show_lines=True,
            highlight=True,
            caption=f"{__title__} {__version__}",
        )

        # columns
        table.add_column(header="#", justify="center")
        table.add_column(header="Nom", justify="left", style="default")
        table.add_column(header="Dimensions", justify="center", style="bright_black")
        table.add_column(header="Score", justify="center", style="magenta")
        table.add_column(header="Chemin CDN", justify="left")
        # table.add_column(header="Syntaxe intégration", justify="right", style="blue")

        # iterate over results
        for r in result[:count]:
            # # syntaxe depending on image type
            # if "logos-icones" in r.get("url"):
            #     syntax = rf"!\[logo {Path(r.get('nom')).stem}]({r.get('url')}){{: .img-rdp-news-thumb }}"
            # else:
            #     syntax = rf"!\[{Path(r.get('nom')).stem}]({r.get('url')})"

            # add row
            table.add_row(
                f"{result.index(r)}",
                f"[link={url_add_utm(r.get('url'))}]{r.get('nom')}[/link]",
                r.get("dimensions"),
                r.get("score"),
                f"[link={defaults_settings.cdn_base_url}/tinyfilemanager.php?p={r.get('cdn_path')}]{r.get('cdn_path')}[/link]",
                # syntax,
            )

        return table
    else:
        return result


@lru_cache
def add_search_criteria_as_str(
    in_txt: str,
    search_filter_dates: Optional[tuple] = None,
    search_results_total: Optional[int] = None,
    search_results_displayed: Optional[int] = None,
    search_term: Optional[str] = None,
    search_filter_type: Optional[str] = None,
    hint: Optional[str] = None,
) -> str:
    """Prettify a title with search criterias.

    Args:
        in_txt: initial title text
        search_filter_dates: tuple of dates used to filter search
        search_results_total: total of results of search. Defaults to None.
        search_results_displayed: total of results to display. Defaults to None.
        search_term: search terms. Defaults to None.
        search_filter_type: search filter type. Defaults to None.
        hint: optional short hint text to display before the table. Defaults to None.

    Returns:
        formatted title
    """
    if all([search_results_displayed, search_results_total]):
        in_txt += f" {search_results_displayed}/{search_results_total} résultats"

    if search_term:
        in_txt += f" avec le terme : {search_term}"

    if any(
        [
            isinstance(search_filter_dates, tuple) and search_filter_dates[0],
            isinstance(search_filter_dates, tuple) and search_filter_dates[1],
            search_filter_type,
        ],
    ):
        in_txt += "\nFiltres : "
        if search_filter_type:
            in_txt += f"de type {search_filter_type}, "
        if isinstance(search_filter_dates, tuple) and search_filter_dates[0]:
            in_txt += f"plus récents que {search_filter_dates[0]:%d %B %Y}, "
        if isinstance(search_filter_dates, tuple) and search_filter_dates[1]:
            in_txt += f"plus anciens que {search_filter_dates[1]:%d %B %Y}"
    else:
        in_txt += "\nAucun filtre de recherche appliqué."

    if hint:
        in_txt += f"\n{hint}"

    return in_txt
