import pickledb
import mysreality.assets as assets
import mysreality.estate_reader as er
import mysreality.sreality as sreality
import urllib.parse
import logging
import mysreality.db as db
from persistqueue import Empty
import datetime
from persistqueue import FIFOSQLiteQueue
from threading import Thread, Lock
import json

import pandas as pd
import time
import pathlib

logger = logging.getLogger("mysreality")


class EstatesAPI:
    def __init__(
        self,
        reactions_db,
        estate_reader,
    ):
        self.rdb = reactions_db
        self.estate_reader = estate_reader

    def _append_reactions(self, df):
        df["reaction"] = None
        reactions = self.rdb.read_all()
        rdf = pd.DataFrame(reactions)
        estates_reactions = {
            k: _user_reactions_text_from_group(x)
            for k, x in rdf.groupby("estate_id")[["username", "reaction"]]
        }

        for estate_id, reaction in estates_reactions.items():
            if estate_id in df.index:
                df.loc[estate_id, "reaction"] = reaction
        return df

    def read(self, date_from=None):
        df = self.estate_reader.read(
            younger_than=date_from,
        )
        df = self._append_reactions(df)

        return df

    def read_estate_reactions(self, estate_uri):
        estate_id = sreality.parse_estate_id_from_uri(estate_uri)
        return self.db.read_by_estate(estate_id)


def uri_to_id(uri):
    if isinstance(uri, urllib.parse.ParseResult):
        url_obj = uri
    else:
        url_obj = urllib.parse.urlparse(uri)

    return f"{url_obj.hostname}{url_obj.path}"


def _user_reactions_text_from_group(x):
    user_reactions = (f"{u}:{r}" for u, r in zip(x["username"], x["reaction"]))
    return ",".join(user_reactions)
