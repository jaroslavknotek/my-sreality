import json
from . import io
import numpy as np
import pathlib
from tqdm.auto import tqdm
import logging
import multiprocessing as mp

logger = logging.getLogger('mysreality')
estate_detail_url_template = "https://www.sreality.cz/api/cs/v2/estates/{}"

def read_estate_ids_from_search(query_params,per_page=60,show_progress = False):
    
    count_uri = f"https://www.sreality.cz/api/cs/v2/estates?{_to_query_string(query_params)}"
    count_res = io.read_request(count_uri)
    count = count_res['result_size']
    
    estate_ids_list = []
    pages = np.arange(np.ceil(count/per_page),dtype=int)
    if show_progress:
        pages = tqdm(pages,desc=f"Collecting {count} estates from pages")
        
    for i in pages:
        qp = query_params.copy()
        qp['per_page']=per_page
        qp['page'] = i+1
        query = _to_query_string(qp)
        
        query_uri=f'https://www.sreality.cz/api/cs/v2/estates?{query}'
        all_json = io.read_request(query_uri)
        estates = all_json['_embedded']['estates']
        estate_hrefs = [e['_links']['self']['href'] for e in estates]
        estate_ids = [int(pathlib.Path(e).parts[-1]) for e in estate_hrefs]
        estate_ids_list.append(estate_ids)
    
    return sum(estate_ids_list,[])

def _to_query_string(query_params):
    return '&'.join([f"{k}={v}"  for k,v in query_params.items()])

def _collect_single_estate(estate_id):
    payload = None
    try:
        payload = io.read_payload(estate_id, estate_detail_url_template)
    except Exception as e:
        logger.warning(f"Could not get estate {estate_id} due to error {e}")
    return payload


def collect_estates(estate_ids):
    with mp.Pool() as pool:
        payloads = list(tqdm(
            pool.imap(_collect_single_estate, estate_ids),
            desc='collecting estates',
            total = len(estate_ids)
        ))
    return [p for p in payloads if p is not None]

def _parse_name(item):
    return item['name']
    
def _parse_value(item):
    value = item['value']
    if isinstance(value,list):
        vals = [ v['value'] for v in value]
        value = ', '.join(vals)
    return value
    
def parse_items(items):
    return {_parse_name(item):_parse_value(item) for item in items}


def payload_to_record(payload):
    data = parse_items(payload['items'])
    
    href = payload['_links']['self']['href']
    estate_id =  pathlib.Path(href).parts[-1]
    data['estate_id'] = estate_id
    data['name'] = payload['locality']['value']
    data['gps_lat'],data['gps_lon'] = payload['map']['lat'],payload['map']['lon']
    
    seo = payload['seo']['locality']
    data['link'] = "https://www.sreality.cz/detail/prodej/dum/rodinny/{}/{}".format(seo,estate_id)
    
    data['uri_api'] = estate_detail_url_template.format(estate_id)
    data['price']=payload['price_czk']['value_raw']
    
    return data