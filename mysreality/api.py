import pickledb
import pathlib
import mysreality.assets as assets
import mysreality.estate_reader as er
import mysreality.sreality as sreality
import urllib.parse
import logging

from persistqueue import Empty
import datetime
from persistqueue import FIFOSQLiteQueue
from threading import Thread, Lock
import json

import time
import pathlib

logger = logging.getLogger('mysreality')
    
def uri_to_id(uri):
    if isinstance(uri,urllib.parse.ParseResult):
        url_obj = uri
    else:
        url_obj = urllib.parse.urlparse(uri)
        
    return f"{url_obj.hostname}{url_obj.path}"

def _intersect_ids(df,ids):
    existing_ids = set(df['estate_id'])
    return list(set(ids) & existing_ids)    


class EstateWatcher():
    def __init__(
        self, 
        estates_api,
        *,
        interval = None,
        timestamp_path = None,
        queue_path = None,
        filter_fn = None,
        download_images = True,
    ):
        queue_path = queue_path or "/tmp/estate_watcher/queue"
        self.queue = FIFOSQLiteQueue(path=queue_path, multithreading=True,auto_commit=True)
        self.estates_api = estates_api
        self.interval = interval or datetime.timedelta(minutes=30)
        self.timestamp_path = pathlib.Path(timestamp_path or '/tmp/estate_watcher/timestamp.txt')
        self.timestamp_path.parent.mkdir(exist_ok=True,parents=True) 
        self.filter_fn = filter_fn
        self.stopping=False
        self.download_images = download_images

    def stop(self,):
        self.stopping = True

    def _can_run(self , timestamp):
        last_ts = self._read_ts() or datetime.datetime.fromtimestamp(1)
        return last_ts,(timestamp-last_ts) > self.interval

    def watch(self):
        t = Thread(target=self._worker)
        logger.warning("Starting estetate watcher")
        t.start()

    def _worker(self,):
        
        while not self.stopping:
            now = datetime.datetime.now()
            last_ts,can_run = self._can_run(now)
            if can_run:
                logger.info('Start reading df at %s',now)
                df = self.estates_api.read_latest(last_ts,images = sel.fdownload_images)
                if self.filter_fn:
                    df = self.filter_fn(df)
                    
                for _,r in df.iterrows():
                    self.queue.put(r.to_json())
                    
                logger.info('Putting %d records to logs',len(df))
                self._update_ts(now)
                
            time.sleep(1)

    def _update_ts(self,ts):
        try:
            with open(self.timestamp_path,'w')as f:
                f.write(str(ts.timestamp()))
        except Exception as e:
            logger.warning("Writing timestamp failed: %s",e)
            
    def _read_ts(self,):
        try:
            with open(self.timestamp_path)as f:
                ts_val = float(f.read().strip())
                return datetime.datetime.fromtimestamp(ts_val)
        except Exception as e: 
            logger.warning("Reading timestamp failed: %s",e)
            return None

    def read_new(self):
        items = []
        while not self.stopping:
            try:
                item = self.queue.get(block=False)
                items.append(json.loads(item))
            except Empty:
                break
        return items
    
class EstatesAPI():
    def __init__(
        self, 
        reaction_db_path, 
        working_dir,
        input_query_params = None,
    ):
        reaction_db_path = pathlib.Path(reaction_db_path)
        reaction_db_path.parent.mkdir(exist_ok=True,parents=True)

        self.db = pickledb.load(reaction_db_path,auto_dump=True)
        self.working_dir = pathlib.Path( working_dir)
        self.working_dir.mkdir(exist_ok=True,parents=True)
        
        if input_query_params is None:
            input_query_params = assets.read_default_sreality_query()
        self.input_query_params = input_query_params
        self.db_lock = Lock()
        

    def read_latest(self,date_from = None, images=True):
        df = er.read_estates(
            self.input_query_params, 
            younger_than = date_from ,
            working_dir = self.working_dir,
            images=images
        )

        df['state_seen'] = None

        with self.db_lock:
            reactions_ids = self.db.getall()
            reactions = [ (uri,self.db.get(uri)) for uri in reactions_ids]
        
        reactions = [ (uri,r) for uri,r in reactions if r]    
        for uri,r in reactions:
            
            estate_id = sreality.parse_estate_id_from_uri(uri)
            if estate_id in df.index:
                value = '/'.join([f"{k}:{v}"for k,v in r.items()])
                df.loc[estate_id,'state_seen'] = value
        
        return df
    
    def write_reaction(self,estate_uri,user,reaction):
        link_id = uri_to_id(estate_uri)
        with self.db_lock:
            record = self.db.get(link_id)
        if record:
            record[user] = reaction
        else:
            record = {user:reaction}
        with self.db_lock:
            self.db.set(link_id,record)
        
    def read_reactions(self,estate_uri):
        link_id = uri_to_id(estate_uri)
        with self.db_lock:
            return self.db.get(link_id)
        