# standard library
import json
from pathlib import Path

local_listing_file = Path().home() / ".geotribu/search/site_content_listing.json"


# with json standard lib
with local_listing_file.open(mode="r", encoding="UTF-8") as j:
    data: dict = json.loads(j.read())

del data["config"]

# print(len(data.get("docs")))

data["docs"] = [
    d for d in data.get("docs") if d.get("location").startswith(("article", "rdp"))
]

# data["docs"] = tuple(
#     filter(lambda c: c.get("location").startswith(("article", "rdp")), data.get("docs"))
# )
# print(len(list(ret)))
# print(len(data.get("docs")))

out_file = local_listing_file.with_name(
    f"{local_listing_file.stem}_filtered_stdlib.json"
)
with out_file.open(mode="w", encoding="UTF-8") as fd:
    json.dump(data, fd, separators=(",", ":"))
