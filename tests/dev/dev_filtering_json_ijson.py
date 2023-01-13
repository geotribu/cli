# standard library
import json
from pathlib import Path

# 3rd party
import ijson

local_listing_file = Path().home() / ".geotribu/search/site_content_listing.json"


out_file = local_listing_file.with_name(
    f"{local_listing_file.stem}_filtered_ijson.json"
)

# with ijson
with local_listing_file.open(mode="rb") as j:

    objects = ijson.items(j, "docs")

    with out_file.open(mode="wb") as fd:
        json.dump(
            tuple(filter(lambda c: c.location.startswith(("article", "rdp")), objects)),
            fd,
            separators=(",", ":"),
        )
