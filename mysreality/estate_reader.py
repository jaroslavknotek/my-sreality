import pandas as pd

from tqdm.auto import tqdm
import multiprocessing as mp

from . import io
from . import sreality
from . import feature_enhancer as fe
import pathlib

import logging 
import datetime

logger = logging.getLogger('mysreality')


def filter_invalid(payloads):
    valid = []
    for p in payloads:
        try:
            _ = sreality.parse_estate_id(p)
            valid.append(p)
        except KeyError:
            logger.debug("Invalid estate %s", p)
    
    return valid


def collect_img_uris_img_paths(payloads,images_dir):
    
    all_img_uris = []
    all_img_paths = []
    for p in payloads:
        estate_id = sreality.parse_estate_id(p)
        img_uris = [ img_node['_links']['self']['href'] for img_node in p['_embedded']['images']]
        all_img_uris.append(img_uris) 

        img_names_w_suffix = [sreality.parse_last_path_part(img_uri) for img_uri in img_uris]
        img_paths = [images_dir/f"{estate_id}"/f"{i:03}_{img_name}" for i,img_name in enumerate(img_names_w_suffix)]
        all_img_paths.append(img_paths)
    
    return sum(all_img_uris,[]),sum(all_img_paths,[])

def di_wrapper(args):
    return io.download_image(*args)
    
def download_images(payloads,images_dir,desc = 'Downloading images'):
    img_uris,img_paths = collect_img_uris_img_paths(payloads,images_dir)
        
    with mp.Pool() as pool:
        _ = list(tqdm(
            pool.imap(di_wrapper, zip(img_uris,img_paths)),
            desc=desc,
            total = len(img_uris)
        ))

def cache_payloads(payloads, working_dir,images = True):
    
    for p in payloads:
        object_id = sreality.parse_estate_id(p)
        payload_path = working_dir/f"{object_id}.json"
        p['mysreality'] = {"saved_timestamp":str(datetime.datetime.now())}
        io.save_json(payload_path,p)        

    if images:
        images_dir = working_dir/'images'
        images_dir.mkdir(parents=True,exist_ok=True
                        )
        download_images(payloads,images_dir)
        
    
def read_estates(query, working_dir,images = True):
    payloads_old = []
    if working_dir:
        payloads_old = read_cached_payloads(working_dir)

    payloads_new = read_payloads(query,existing_payloads = payloads_old)
    payloads_new = filter_invalid(payloads_new)

    if working_dir:
        logger.info("Saving new payloads")
        cache_payloads(payloads_new,working_dir,images=images)
        
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
