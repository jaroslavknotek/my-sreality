import pandas as pd

from . import io
from . import sreality
from . import feature_enhancer as fe
import pathlib

import logging 

logger = logging.getLogger('mysreality')

def read_estates(query, working_dir):
    payloads_old = []
    if working_dir:
        payloads_old = read_cached_payloads(working_dir)

    payloads_new = read_payloads(query,existing_payloads = payloads_old)

    if working_dir:
        logger.info("Saving new payloads")
        for p in payloads_new:
            object_id = sreality.parse_estate_id(p)
            payload_path = working_dir/f"{object_id}.json"
            io.save_json(payload_path,p)
    payloads = payloads_new + payloads_old
    
    df = to_dataframe(payloads)
    df = fe.add_distance(df)
    df = fe.score_estates(df)

    df['id'] = df['estate_id']
    df = df.set_index('id')
    return df


def read_cached_payloads(payloads_dir):
    payloads_dir = pathlib.Path(payloads_dir)
    payloads_paths = list(payloads_dir.glob('*.json'))
    return [ io.load_json(p) for p in  payloads_paths]

def read_payloads_summary(payloads):
    return {
        int(pathlib.Path(p['_links']['self']['href']).parts[-1]):p['price_czk']['value_raw'] 
        for p in payloads
    }

def read_payloads(query,existing_payloads= None):
    estates = sreality.read_estate_ids_from_search(query,show_progress=True)
    excluded_ids = []
    if existing_payloads:
        existing = read_payloads_summary(existing_payloads)
        for estate_id,new_price in estates.items():
            existing_price = existing.get(estate_id,None)
            if existing_price == new_price:
                excluded_ids.append(estate_id)

    if len(excluded_ids) > 0 :
        logger.info("Some estates were already downloaded. (%s)",len(excluded_ids))

    estate_ids = estates.keys()
    estate_ids = list(set(estate_ids) - set(excluded_ids))
    
    return sreality.collect_estates(estate_ids)
    

def to_dataframe(payloads):
    records = []
    for payload in payloads:
        record = sreality.payload_to_record(payload)
        records.append(record)
    return pd.DataFrame(records)
