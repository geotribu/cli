#! python3  # noqa E265

"""
    Usage from the repo root folder:

    .. code-block:: bash
        pytest
"""

# standard
from datetime import datetime
from pathlib import Path

# 3rd party
import pytest

# project
from geotribu_cli import __about__, cli
from geotribu_cli.constants import GeotribuDefaults
from geotribu_cli.utils.slugger import sluggy

# ############################################################################
# ########## Globals #############
# ################################

defaults_settings = GeotribuDefaults()

# ############################################################################
# ########## Classes #############
# ################################


@pytest.mark.parametrize("option", ("-h", "--help"))
def test_cli_help(capsys, option):
    """Test CLI help."""
    with pytest.raises(SystemExit):
        cli.main([option])

    out, err = capsys.readouterr()

    assert (
        f"{__about__.__title__} {__about__.__version__} - {__about__.__summary__}"
        in out
    )
    assert err == ""


@pytest.mark.parametrize("option", (["--version"]))
def test_cli_version(capsys, option):
    """Test CLI version."""
    with pytest.raises(SystemExit):
        cli.main([option])

    out, err = capsys.readouterr()

    assert f"{__about__.__version__}\n" == out

    assert err == ""


def test_cli_run_comments_latest(capsys):
    """Test nested subcommand comments latest."""
    cli.main(["comments", "latest"])

    out, err = capsys.readouterr()

    assert err == ""
    assert Path(Path().home() / ".geotribu/comments/latest.json").exists()


def test_cli_run_comments_open(capsys):
    """Test nested subcommand comments latest."""
    cli.main(["comments", "open"])

    out, err = capsys.readouterr()

    assert err == ""
    assert Path(Path().home() / ".geotribu/comments/latest.json").exists()


@pytest.mark.flaky(retries=3, delay=5, only_on=[SystemExit])
def test_cli_run_comments_open_specific(capsys):
    """Test nested subcommand comments latest."""
    cli.main(
        [
            "comments",
            "open",
            "--page-size",
            "100",
            "--comment-id",
            "15",
            "--expiration-rotating-hours",
            "0",
            "-vv",
        ]
    )

    out, err = capsys.readouterr()

    assert err == ""
    assert Path(Path().home() / ".geotribu/comments/latest.json").exists()


def test_cli_run_contenus_articles_ubuntu(capsys):
    """Test CLI images."""
    cli.main(
        [
            "search-content",
            "-f",
            "article",
            "-o",
            "table",
            "title:ubuntu",
            "--no-prompt",
        ]
    )

    out, err = capsys.readouterr()

    # assert out.startswith("[")
    assert err == ""

    assert Path(Path().home() / ".geotribu/search/site_search_index.json").exists()


def test_cli_run_images_logo_news(capsys):
    """Test CLI images."""
    cli.main(["search-image", "--no-prompt", "-o", "json", "-f", "logo", "news"])

    out, err = capsys.readouterr()

    assert out.startswith("[")
    assert err == ""

    assert Path(Path().home() / ".geotribu/search/cdn_search_index.json").exists()


def test_cli_run_si_post_table(capsys):
    """Test CLI images."""
    cli.main(["si", "--no-prompt", "post*"])

    out, err = capsys.readouterr()

    assert out.strip().startswith("Recherche dans les images")
    assert err == ""

    assert Path(Path().home() / ".geotribu/search/cdn_search_index.json").exists()


def test_cli_run_new_article(capsys):
    """Test subcommand creating new article."""

    art_title = f"Test Unitaire de {__about__.__title__} {__about__.__version__}"

    cli.main(
        [
            "new",
            "article",
            "--date",
            f"{datetime.today():%Y-%m-%d}",
            "--titre",
            art_title,
            "--stay",
        ]
    )

    out, err = capsys.readouterr()

    out_file = defaults_settings.geotribu_working_folder.joinpath(
        f"drafts/{datetime.today():%Y-%m-%d}_{sluggy(art_title)}.md"
    )

    assert err == ""
    assert (
        out_file.parent.is_dir()
    ), f"Le dossier {out_file.parent} devrait avoir été créé"
    assert out_file.is_file(), f"Le fichier {out_file} devrait avoir été créé"

    # clean up
    out_file.unlink(missing_ok=True)


def test_cli_run_rss(capsys):
    """Test subcommand rss."""
    cli.main(["rss", "--no-prompt", "-o", "table"])

    out, err = capsys.readouterr()

    assert err == ""
