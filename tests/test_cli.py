#! python3  # noqa E265

"""
    Usage from the repo root folder:

    .. code-block:: bash
        pytest
"""

from pathlib import Path

# 3rd party
import pytest

# project
from geotribu_cli import __about__, cli

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


def test_cli_run_contenus_articles_ubuntu(capsys):
    """Test CLI images."""
    cli.main(["search-content", "-f", "article", "-o", "table", "title:ubuntu"])

    out, err = capsys.readouterr()

    # assert out.startswith("[")
    assert err == ""

    assert Path(Path().home() / ".geotribu/search/site_search_index.json").exists()


def test_cli_run_images_logo_news(capsys):
    """Test CLI images."""
    cli.main(["images", "-o", "json", "-f", "logo", "news"])

    out, err = capsys.readouterr()

    assert out.startswith("[")
    assert err == ""

    assert Path(Path().home() / ".geotribu/search/cdn_search_index.json").exists()


def test_cli_run_rss(capsys):
    """Test subcommand rss."""
    cli.main(["rss", "-o", "table"])

    out, err = capsys.readouterr()

    assert err == ""
