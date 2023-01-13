# standard library
import json
from pathlib import Path

from msgspec import Struct
from msgspec.json import decode, encode

local_listing_file = Path().home() / ".geotribu/search/site_content_listing.json"


class Configuration(Struct):
    lang: list
    separator: str


class Document(Struct):
    title: str
    text: str
    location: str
    tags: list


class Listing(Struct):
    config: Configuration
    docs: list[Document]


with local_listing_file.open("r", encoding="UTF-8") as f:
    data = decode(f.read(), type=Listing)

# del data["config"]

out_data = tuple(filter(lambda c: c.location.startswith(("article", "rdp")), data.docs))

out_file = local_listing_file.with_name(
    f"{local_listing_file.stem}_filtered_msgspec.json"
)
with out_file.open(mode="w", encoding="UTF-8") as fd:
    json.dump(encode(out_data), fd, separators=(",", ":"))
