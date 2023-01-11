#! python3  # noqa E265

"""
    Usage from the repo root folder:

    .. code-block:: bash
        pytest
"""


# 3rd party
import pytest

# project
from geotribu_cli import __about__, cli

# ############################################################################
# ########## Classes #############
# ################################


def test_cli_run_rss(capsys):
    """Test subcommand rss."""
    with pytest.raises(SystemExit):
        cli.main(["rss", "-o", "table"])

        out, err = capsys.readouterr()
        print(out)

        assert out == ""
        assert err == ""


def test_cli_help(capsys):
    """Test CLI help."""
    with pytest.raises(SystemExit):
        cli.main(["--help"])

        out, err = capsys.readouterr()

        assert __about__.__cli_usage__ in out
        assert err == ""


def test_cli_version(capsys):
    """Test CLI version."""
    with pytest.raises(SystemExit):
        cli.main(["--version"])

        out, err = capsys.readouterr()

        assert out[0] == f"{__about__.__version__}\n"
        assert err == ""
