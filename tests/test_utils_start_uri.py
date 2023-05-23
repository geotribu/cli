# standard library
from unittest.mock import patch

# package
from geotribu_cli.utils.start_uri import open_uri


def describe_startfile():
    @patch("subprocess.call")
    @patch("os.startfile", create=True)
    def with_file(mock_startfile, mock_call, tmp_path, expect):
        path = tmp_path / "example.txt"
        path.write_text("Hello, world!")

        open_uri(path)
        expect(mock_startfile.call_count + mock_call.call_count) == 1

    @patch("webbrowser.open")
    def with_url(mock_open, expect):
        open_uri("http://example.com")
        expect(mock_open.call_count) == 1
