#! python3  # noqa: E265 F401

# submodules
from geotribu_cli.comments import parser_comments_broadcast  # noqa: F401
from geotribu_cli.comments import parser_comments_latest  # noqa: F401
from geotribu_cli.comments import parser_comments_read  # noqa: F401
from geotribu_cli.content.header_check import parser_header_check  # noqa: F401
from geotribu_cli.content.new_article import parser_new_article  # noqa: F401
from geotribu_cli.images.images_optimizer import parser_images_optimizer  # noqa: F401
from geotribu_cli.rss.rss_reader import parser_latest_content  # noqa: F401
from geotribu_cli.search.search_content import parser_search_content  # noqa: F401
from geotribu_cli.search.search_image import parser_search_image  # noqa: F401
from geotribu_cli.social.cmd_mastodon_export import parser_mastodon_export  # noqa: F401

from .open_result import parser_open_result  # noqa: F401
from .upgrade import parser_upgrade  # noqa: F401
