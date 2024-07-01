import pickledb

import mysreality.assets as assets
import mysreality.estate_reader as er
import mysreality.sreality as sreality
import urllib.parse
import logging

logger = logging.getLogger('mysreality')
    
def uri_to_id(uri):
    if isinstance(uri,urllib.parse.ParseResult):
        url_obj = uri
    else:
        url_obj = urllib.parse.urlparse(uri)
        
    return f"{url_obj.hostname}{url_obj.path}"
    
# def filter_later_than(df,dt):
#     ts_from = dt.strftime('%Y%m%d%H%M%S')
#     return df[df['timestamp'] > ts_from]

def _intersect_ids(df,ids):
    existing_ids = set(df['estate_id'])
    return list(set(ids) & existing_ids)    
    
class EstatesAPI():
    def __init__(self, reaction_db_path, working_dir,input_query_params = None):
        self.db = pickledb.load(reaction_db_path,auto_dump=True)
        self.working_dir = working_dir
        if input_query_params is None:
            input_query_params = assets.read_default_sreality_query()
        self.input_query_params = input_query_params
        
    def read_latest(self,date_from):
        df = er.read_estates(
            self.input_query_params, 
            younger_than = date_from ,
            working_dir = self.working_dir
        )

        df['state_seen'] = None
        for uri in self.db.getall():
            v = self.db.get(uri)
            if not v: # if it was deleted in during execution
                continue
            
            estate_id = sreality.parse_estate_id_from_uri(uri)
            if estate_id in df.index:
                value = '/'.join([f"{k}:{v}"for k,v in v.items()])
                df.loc[estate_id,'state_seen'] = value
        
        return df
    
    def write_reaction(self,estate_uri,user,reaction):
        link_id = uri_to_id(estate_uri)
        record = self.db.get(link_id)
        if record:
            record[user] = reaction
        else:
            record = {user:reaction}
        self.db.set(link_id,record)
        
    def read_reactions(self,estate_uri):
        link_id = uri_to_id(estate_uri)
        return self.db.get(link_id)
        