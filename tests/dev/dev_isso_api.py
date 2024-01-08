from pprint import pprint

import requests

isso_url = "https://comments.geotribu.fr/"

# r = requests.get(f"{isso_url}latest", params={"limit": 2})
# r.raise_for_status()

# pprint(r.json())

# r = requests.get(f"{isso_url}config")
# r.raise_for_status()

# pprint(r.json())

s = requests.Session()

r = s.get(f"{isso_url}admin", auth=("admin", "xxxxxx"))
r.raise_for_status()

z = s.get(f"{isso_url}")

print(r)
