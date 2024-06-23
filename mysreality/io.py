import urllib.request
import json
   
    
def read_request(url):
    response = urllib.request.urlopen(url)
    payload_raw = response.read()
    return json.loads(payload_raw)
    
def read_payload(estate_id,url_base):
    url = url_base.format(estate_id)
    return read_request(url)

def save_json(path,data):
    with open(path,'w') as f:
        json.dump(data,f)

def load_json(path):
    with open(path,'r') as f:
        return json.load(f)
    