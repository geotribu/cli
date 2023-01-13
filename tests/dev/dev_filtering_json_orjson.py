# standard library
from pathlib import Path

# 3rd party
import orjson

local_listing_file = Path().home() / ".geotribu/search/site_content_listing.json"


# with json standard lib
with local_listing_file.open(mode="rb") as j:
    data: dict = orjson.loads(j.read())

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
    f"{local_listing_file.stem}_filtered_orjson.json"
)
with out_file.open(mode="wb") as fd:
    fd.write(orjson.dumps(data))
