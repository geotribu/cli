#! python3  # noqa: E265

# submodules
from geotribu_cli.comments import (  # noqa: F401
    parser_comments_broadcast,
    parser_comments_latest,
)

from .images_optimizer import parser_images_optimizer  # noqa: F401
from .open_result import parser_open_result  # noqa: F401
from .rss_reader import parser_latest_content  # noqa: F401
from .search_content import parser_search_content  # noqa: F401
from .search_image import parser_search_image  # noqa: F401
from .upgrade import parser_upgrade  # noqa: F401
