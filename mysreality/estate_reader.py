import pandas as pd

from tqdm.auto import tqdm
import multiprocessing as mp
from . import assets
from . import db
from . import io
from . import sreality
from . import feature_enhancer as fe
from . import utils
import pathlib

import logging
import datetime

logger = logging.getLogger("mysreality")


class DummyDfWrapper(pd.DataFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getitem__(self, key):
        if isinstance(key, str) and key not in self.columns:
            # create column
            self[key] = None

        ret = super().__getitem__(key)
        if isinstance(ret, pd.DataFrame):
            return DummyDfWrapper(columns=self.columns)
        else:
            return ret


class EstateReader:
    def __init__(
        self,
        estates_data_path,
        input_query_params=None,
        download_images=True,
        notify_progress=True,
    ):
        if input_query_params is None:
            input_query_params = assets.read_default_sreality_query()

        estates_data_path = pathlib.Path(estates_data_path)
        self.input_query_params = input_query_params
        self.estates_db = db.EstatesDb(estates_data_path)
        self.download_images = download_images
        self.images_dir = estates_data_path / "images"
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.notify_progress = notify_progress

    def read(self, younger_than=None):
        payloads_old = self.estates_db.read_all()
        payloads_new = self.sync_new(existing=payloads_old)

        payloads = payloads_new + payloads_old
        if younger_than:
            ts_from = younger_than.strftime("%Y%m%d%H%M%S")
            payloads = [
                p
                for p in payloads
                if p.get("mysreality", {}).get("saved_timestamp", "9") >= ts_from
            ]

        if len(payloads) == 0:
            return DummyDfWrapper()

        logger.info("Converting payloads to dataframe.")
        df = to_dataframe(payloads)
        df = fe.add_distance(df)
        df = fe.score_estates(df)

        df["id"] = df["estate_id"]
        df = df.set_index("id")
        df["Plocha pozemku"] = df["Plocha pozemku"].astype(int)
        return df

    def sync_new(self, existing=None):
        payloads = read_payloads(self.input_query_params, existing_payloads=existing)
        payloads = filter_invalid(payloads)
        self.cache_payloads(payloads)
        return payloads

    def cache_payloads(self, payloads):
        logger.info("Saving new payloads")
        for p in payloads:
            self.estates_db.write(p)

        if self.download_images:
            download_images(payloads, self.images_dir, progress=self.notify_progress)


def _di(args):
    return io.download_image(*args)


def download_images(payloads, images_dir, desc="Downloading images", progress=True):
    img_uris, img_paths = collect_img_uris_img_paths(payloads, images_dir)

    args = list(zip(img_uris, img_paths))
    _ = utils.parallel(_di, args, desc=desc, progress=progress)


def collect_img_uris_img_paths(payloads, images_dir):
    all_img_uris = []
    all_img_paths = []
    for p in payloads:
        estate_id = sreality.parse_estate_id(p)
        img_uris = [
            img_node["_links"]["self"]["href"] for img_node in p["_embedded"]["images"]
        ]
        all_img_uris.append(img_uris)

        img_names_w_suffix = [
            sreality.parse_last_path_part(img_uri) for img_uri in img_uris
        ]
        img_paths = [
            images_dir / f"{estate_id}" / f"{i:03}_{img_name}"
            for i, img_name in enumerate(img_names_w_suffix)
        ]
        all_img_paths.append(img_paths)

    return sum(all_img_uris, []), sum(all_img_paths, [])


def read_payloads_summary(payloads):
    return {
        sreality.parse_estate_id(p): p.get("price_czk", {}).get("value_raw", None)
        for p in payloads
    }


def to_dataframe(payloads):
    records = []
    for payload in payloads:
        record = sreality.payload_to_record(payload)
        if record is None:
            continue
        ts = payload.get("mysreality", {}).get("saved_timestamp", "")
        record["timestamp"] = ts
        records.append(record)
    return pd.DataFrame(records)


def filter_invalid(payloads):
    valid = []
    for p in payloads:
        try:
            _ = sreality.parse_estate_id(p)
            valid.append(p)
        except KeyError:
            logger.debug("Invalid estate %s", p)

    return valid


def read_payloads(query, existing_payloads=None):
    estates = sreality.read_estate_ids_from_search(query, show_progress=True)
    excluded_ids = []
    if existing_payloads:
        existing = read_payloads_summary(existing_payloads)
        for estate_id, new_price in estates.items():
            existing_price = existing.get(estate_id, None)
            if existing_price == new_price:
                excluded_ids.append(estate_id)

    if len(excluded_ids) > 0:
        logger.info("Some estates were already downloaded. (%s)", len(excluded_ids))

    estate_ids = estates.keys()
    estate_ids = list(set(estate_ids) - set(excluded_ids))

    payloads = sreality.collect_estates(estate_ids)
    for p in payloads:
        ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        p["mysreality"] = {"saved_timestamp": ts}

    return payloads
