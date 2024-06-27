import requests
import json
import pathlib

import logging

logger = logging.getLogger('mysreality')

def read_request(url,headers = None):
    logger.debug("Request: %s", url)

    if headers is None:
        # HACK: without this sreality api returns different prices (ts:20240617)
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0"
        }
    res = requests.get(url,headers =headers)
    return res.json()

def save_json(path,data):
    with open(path,'w') as f:
        json.dump(data,f)

def load_json(path):
    with open(path,'r') as f:
        return json.load(f)

def download_image(image_uri,destination_path):
    try:
        pathlib.Path(destination_path).parent.mkdir(exist_ok=True,parents=True)
        img_data = requests.get(image_uri).content
        with open(destination_path, 'wb') as handler:
            handler.write(img_data)
    except Exception as e:
        logger.warning("Image was not saved %s. Error: %s",image_uri,e)
