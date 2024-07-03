from . import io
import numpy as np
import pathlib
from tqdm.auto import tqdm
import logging
import multiprocessing as mp

from urllib.parse import urlparse

logger = logging.getLogger("mysreality")
estate_detail_url_template = "https://www.sreality.cz/api/cs/v2/estates/{}"


def read_estate_ids_from_search(query_params, per_page=60, show_progress=False):
    count_uri = (
        f"https://www.sreality.cz/api/cs/v2/estates?{_to_query_string(query_params)}"
    )
    count_res = io.read_request(count_uri)
    count = count_res["result_size"]

    estate_ids_list = []
    prices_list = []
    pages = np.arange(np.ceil(count / per_page), dtype=int)
    if show_progress:
        pages = tqdm(pages, desc=f"Collecting {count} estates from pages")

    uris = []
    for page in pages:
        qp = query_params.copy()
        qp["per_page"] = per_page
        qp["page"] = page + 1
        query = _to_query_string(qp)

        query_uri = f"https://www.sreality.cz/api/cs/v2/estates?{query}"
        uris.append(query_uri)

    payloads = _paralel_requests(uris)
    for all_json in payloads:
        estates = all_json["_embedded"]["estates"]
        estate_hrefs = [e["_links"]["self"]["href"] for e in estates]
        estate_ids = [int(pathlib.Path(e).parts[-1]) for e in estate_hrefs]
        estate_ids_list.append(estate_ids)

        prices = [p["price_czk"]["value_raw"] for p in estates]
        prices_list.append(prices)

    e = np.concatenate(estate_ids_list)
    p = np.concatenate(prices_list)
    return {k: v for k, v in zip(e, p)}


def _to_query_string(query_params):
    return "&".join([f"{k}={v}" for k, v in query_params.items()])


def _request_payload(url):
    payload = None
    try:
        payload = io.read_request(url)
    except Exception as e:
        logger.warning(f"Could not get estate {url} due to error {e}")
    return payload


def _paralel_requests(uris, desc=None):
    with mp.Pool() as pool:
        payloads = list(
            tqdm(pool.imap(_request_payload, uris), desc=desc, total=len(uris))
        )
    return [p for p in payloads if p is not None]


def collect_estates(estate_ids):
    uris = [estate_detail_url_template.format(estate_id) for estate_id in estate_ids]
    return _paralel_requests(uris, desc="collecting estates")


def _parse_name(item):
    return item["name"]


def _parse_value(item):
    value = item["value"]
    if isinstance(value, list):
        vals = [v["value"] for v in value]
        value = ", ".join(vals)
    return value


def parse_items(items):
    return {_parse_name(item): _parse_value(item) for item in items}


def parse_estate_id(payload):
    href = payload["_links"]["self"]["href"]
    return parse_estate_id_from_uri(href)


def payload_to_record(payload):
    data = parse_items(payload["items"])

    estate_id = parse_estate_id(payload)
    data["estate_id"] = estate_id
    data["name"] = payload["locality"]["value"]
    data["gps_lat"], data["gps_lon"] = payload["map"]["lat"], payload["map"]["lon"]

    seo = payload["seo"]["locality"]
    data["link"] = "https://www.sreality.cz/detail/prodej/dum/rodinny/{}/{}".format(
        seo, estate_id
    )

    data["uri_api"] = estate_detail_url_template.format(estate_id)
    data["price"] = payload["price_czk"]["value_raw"]

    return data


def parse_last_path_part(maybe_uri_text):
    uri_text = str(maybe_uri_text)
    return urlparse(uri_text).path.split("/")[-1]


def parse_estate_id_from_uri(maybe_uri_text):
    estate_id_text = parse_last_path_part(maybe_uri_text)
    return int(estate_id_text)
