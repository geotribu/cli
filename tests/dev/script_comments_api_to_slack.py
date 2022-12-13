#! python3  # noqa: E265

"""
    Send a structured message to Slack through a webhook.
    Using the Block Builder kit: https://api.slack.com/tools/block-kit-builder
"""

# #############################################################################
# ########## LIBRARIES #############
# ##################################

# standard library
import json
import logging
import warnings
from datetime import datetime
from os import environ

# 3rd party
from requests import HTTPError, Session

# #############################################################################
# ########## GLOBALS ###############
# ##################################

COMMENTS_API_URL = "https://comments.geotribu.fr/latest?limit=10"
logger = logging.getLogger(__name__)
headers = {
    'User-Agent': 'geotribot/0.1.0',
    'From': 'bot@geotribu.fr'
}


# #############################################################################
# ########## Main ##################
# ##################################

# retrieve latest comments
with Session() as requests_session:
    response = requests_session.get(url=COMMENTS_API_URL)
    # check request response
    try:
        response.raise_for_status()
        logging.debug(f"URL check passed for: {COMMENTS_API_URL}")
    except HTTPError as err:
        logger.error("Something wrong happened: {}".format(err))

comments = response.json()
print(len(comments))

print(comments[-1])
