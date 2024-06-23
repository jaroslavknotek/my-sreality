import urllib.request
import json
   
    
def read_request(url):
    response = urllib.request.urlopen(url)
    payload_raw = response.read()
    return json.loads(payload_raw)
    
def read_payload(estate_id,url_base):
    url = url_base.format(estate_id)
    return read_request(url)
