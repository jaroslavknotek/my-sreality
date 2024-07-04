from . import assets
from . import estate_reader as er
from . import sreality
from . import db

import urllib.parse
import logging

from datetime import datetime, timedelta
from threading import Thread, Lock
import json

import time
import pathlib

logger = logging.getLogger("mysreality")


class EstateWatcher:
    def __init__(
        self,
        estates_api,
        timestamper,
        queue,
        *,
        interval_minutes=None,
        filter_fn=None,
        download_images=True,
    ):
        self.queue = queue
        self.estates_api = estates_api
        self.interval = timedelta(minutes=interval_minutes or 30)

        self.timestamper = timestamper
        self.filter_fn = filter_fn
        self.stopping = False
        self.download_images = download_images

    def stop(self):
        self.stopping = True

    def _can_run(self, timestamp):
        last_ts = self.timestamper.read() or datetime.fromtimestamp(1)
        return last_ts, (timestamp - last_ts) > self.interval

    def watch(self):
        t = Thread(target=self._worker, daemon=True)
        t.start()

    def sync(self):
        try:
            now = datetime.now()
            last_ts, can_run = self._can_run(now)
            if can_run:
                logger.info("Start reading df at %s, last ts:(%s)", now, last_ts)
                df = self.estates_api.read(date_from=last_ts)

                if self.filter_fn:
                    df = self.filter_fn(df)

                logger.info("Putting %d records to queue", len(df))
                for _, r in df.iterrows():
                    self.queue.put(r.to_dict())

                logger.info("Writing Timestamp %s", now)
                self.timestamper.update(now)
        except (KeyboardInterrupt, SystemExit):
            logger.info("Shutting down the watcher")
            self.stopping = True
            raise
        except Exception as e:
            logger.exception("Reading estates exception")

    def _worker(self):
        logger.info("Starting estate watcher")
        while not self.stopping:
            self.sync()
            # check if it's time to run every n seconds
            time.sleep(1)
