#! python3  # noqa: E265

"""
    Tools related to geometry and geographic stuff.

    Author: Julien Moura (github.com/guts)
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import base64
import logging
import zlib
from sqlite3 import Connection

# #############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)


# #############################################################################
# ########## Classes ###############
# ##################################


class GeomTools:
    """Tools related to geometry and geographic objects."""

    def __init__(self, db_type: str = "spatialite"):
        """Instanciation method."""

    @staticmethod
    def encode_geom(wkb_geom: bytes) -> str:
        """Encode geometry into base 64.

        Args:
            wkb_geom (str): geometry to encode (WKT)

        Returns:
            bytes: encoded geometry (WKB)
        """
        return base64.b64encode(zlib.compress(wkb_geom)).decode("ascii")

    @staticmethod
    def decode_geom(wkb_encoded: str) -> bytes:
        """Decode encoded geometry.

        Args:
            wkb_encoded (str): input geometry to decode

        Returns:
            bytes: decoded geometry
        """
        return zlib.decompress(base64.b64decode(wkb_encoded))

    @staticmethod
    def within(
        wkb_1: bytes, wkb_2: bytes, db_connection: Connection, encoded: bool = False
    ) -> bool:
        """Returns True if geom wkb_1 is within geom wkb_2. Require a spatialite
        connection (through DatabaseManager) to run the test.

        Args:
            wkb_1 (bytes): first geometry as WKB
            wkb_2 (bytes): second geometry as WKB
            db_connection (Connection): opened connection to a SpatiaLite database
            encoded (bool, optional): if geometries need to be decoded. Defaults to False.

        Returns:
            bool: True if wkb_1 is within wkb_2
        """
        # TODO : Add projection
        logger.debug("Testing WITHIN predicate with spatialite")
        if encoded:
            wkb_1 = GeomTools.decode_geom(wkb_1)
            wkb_2 = GeomTools.decode_geom(wkb_2)

        query = (
            "SELECT ST_Within(ST_GeomFromWKB(x'%s'), ST_GeomFromWKB(x'%s')) AS test"
            % (
                wkb_1.hex(),
                wkb_2.hex(),
            )
        )
        # logger.debug(query)
        cursor = db_connection.cursor()
        cursor.execute(query)
        row = cursor.fetchone()

        return row["test"] == 1


# #############################################################################
# ##### Main #######################
# ##################################
if __name__ == "__main__":
    pass
