import pandas as pd

from . import io
from . import sreality
from . import feature_enhancer as fe

import logging 

logger = logging.getLogger('mysreality')

def read_estates(query, working_dir):

    # TODO read existing and extract 

    excluded_ids = None
    payloads_old = []
    if working_dir:
        payloads_paths = list(working_dir.glob('*.json'))
        payloads_old = [ io.load_json(p) for p in  payloads_paths]
        excluded_ids = [ int(p.stem) for p in payloads_paths]

    payloads_new = read_payloads(query,excluded_ids = excluded_ids)

    if working_dir:
        logger.info("Saving new payloads")
        for p in payloads_new:
            object_id = sreality.parse_estate_id(p)
            payload_path = working_dir/f"{object_id}.json"
            io.save_json(payload_path,p)
    payloads = payloads_new + payloads_old
        
        
            
    # TODO save new payloads

    df = to_dataframe(payloads)
    df = fe.add_distance(df)
    df = fe.score_estates(df)

    return df

def read_payloads(query,excluded_ids= None):
    estate_ids = sreality.read_estate_ids_from_search(query,show_progress=True)

    if excluded_ids:
        estate_ids = list(set(estate_ids) - set(excluded_ids))
        logger.info(f"Some estates were already downloaded({len(excluded_ids)}).")
    
    return sreality.collect_estates(estate_ids)
    

def to_dataframe(payloads):
    records = []
    for payload in payloads:
        record = sreality.payload_to_record(payload)
        records.append(record)
    return pd.DataFrame(records)
