import pandas as pd

from . import sreality
from . import feature_enhancer as fe

from tqdm.auto import tqdm

def read_estates(query):


    # TODO read existing and extract 
    excluded_ids = None
    payloads = read_payloads(query,excluded_ids = excluded_ids)

    # TODO save new payloads

    df = to_dataframe(payloads)
    df = fe.add_distance(df)
    df = fe.score_estates(df)

    return df

def read_payloads(query,excluded_ids= None):
    estate_ids = sreality.read_estate_ids_from_search(query,show_progress=True)

    if excluded_ids is not None:
        estate_ids = set(estate_ids) - set(excluded_ids)
    
    return sreality.collect_estates(estate_ids)
    

def to_dataframe(payloads):
    records = []
    for payload in payloads:
        record = sreality.payload_to_record(payload)
        records.append(record)
    return pd.DataFrame(records)

