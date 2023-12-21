import json
from pathlib import Path
from pprint import pprint

import requests
from extruct.jsonld import JsonLdExtractor
from extruct.opengraph import OpenGraphExtractor
from w3lib.html import get_base_url

from geotribu_cli.utils.slugger import sluggy

opengraphe = OpenGraphExtractor()
ogp_folder = Path("metadata")
ogp_folder.mkdir(parents=True, exist_ok=True)

environments_urls = {
    "localhost": "http://127.0.0.1:8000/"
    "prod": "https://geotribu.fr/",
    "preprod": "https://preview-pullrequest-917--geotribu-preprod.netlify.app/",
}

comparison_contents = {
    "custom_rdp_2023-07": "rdp/2023/rdp_2023-07-28/",
    "custom_article": "articles/2023/2023-10-16_panoramax-bilan-phase-construction/",
    "social_article": "articles/2023/2023-09-09_tutoriel-geolocalisation-haute-precision/",
}

responses: list[requests.Response] = []

for environment_name, base_url in environments_urls.items():
    for content_key, content_path in comparison_contents.items():
        response = requests.get(url=f"{base_url}{content_path}")
        ogp_data = opengraphe.extract(
            htmlstring=response.text,
            base_url=get_base_url(text=response.text, baseurl=response.url),
        )
        ogp_folder.joinpath((f"ogp_{content_key}_{environment_name}.json")).write_text(
            json.dumps(ogp_data, sort_keys=True, indent=4)
        )


# -- Compare --

# # OGP


# for response in responses:


# # assert ogp_data_prod == ogp_data_preprod

# jld_extractor = JsonLdExtractor()
# jld_data_prod = jld_extractor.extract(htmlstring=resp_prod.text, base_url=base_url_prod)
# jld_data_preprod = jld_extractor.extract(
#     htmlstring=resp_preprod.text, base_url=base_url_preprod
# )
# Path("jld_prod.json").write_text(json.dumps(jld_data_prod, sort_keys=True, indent=4))
# Path("jld_preprod.json").write_text(
#     json.dumps(jld_data_preprod, sort_keys=True, indent=4)
# )
# assert jld_data_prod == jld_data_preprod
