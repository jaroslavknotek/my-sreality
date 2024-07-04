import os
from . import io
from . import sreality
import typing
import pathlib
import shutil
import logging
import json
from datetime import datetime
import uuid

logger = logging.getLogger("mysreality")


class TimestampPersitor:
    def __init__(self, timestamp_path):
        self.timestamp_path = pathlib.Path(timestamp_path)
        self.timestamp_path.parent.mkdir(exist_ok=True, parents=True)

    def update(self, ts):
        try:
            with open(self.timestamp_path, "w") as f:
                f.write(str(ts.timestamp()))
        except Exception as e:
            logger.warning("Writing timestamp failed: %s", e)

    def read(self):
        try:
            with open(self.timestamp_path) as f:
                ts_val = float(f.read().strip())
                return datetime.fromtimestamp(ts_val)
        except Exception as e:
            logger.warning("Reading timestamp failed: %s", e)
            return None


class DiscoveredQueue:
    def __init__(self, discovery_path):
        self.db = FileSystemDb(discovery_path, is_json=True)

    def put(self, obj):
        fn = _unique_orderable_fn()
        content = {"data": obj}
        self.db.write(fn, content)

    def pop(self):
        item = self.db.pop()
        if item:
            return item["data"]
        else:
            return None

    def total(self):
        names = self.db.read_names(sorted_=False)
        return len(names)


def _unique_orderable_fn():
    ts = datetime.now().strftime("%Y%m%d%H%M%S.%f")
    uuid_str = str(uuid.uuid4())
    return f"{ts}_{uuid_str}"


class EstatesDb:
    def __init__(self, db_path):
        self.db = FileSystemDb(db_path, is_json=True)

    def read_all(self):
        items = self.db.read_all()
        return [item for item in items.values()]

    def write(self, estate: dict):
        estate_id = sreality.parse_estate_id(estate)
        filename = f"{estate_id}.json"
        self.db.write(filename, estate)

    def read(self, estate_id: int):
        filename = f"{estate_id}.json"
        return self.db.read(filename)


def _format_reaction_filename(estate_id, username):
    return f"{estate_id}_{username}.txt"


def _map_reaction(item):
    record_id, content = item
    # assuming estate id does not contain '_'
    splitter_index = record_id.index("_")
    username = record_id[splitter_index + 1 :]
    estate_id = int(record_id[:splitter_index])
    return Reaction(username, estate_id, content)


class Reaction(typing.NamedTuple):
    username: str
    estate_id: int
    reaction: str


class ReactionsDb:
    def __init__(self, db_path):
        self.db = FileSystemDb(db_path)

    def write(self, estate_id, username, reaction):
        filename = _format_reaction_filename(estate_id, username)
        self.db.write(filename, reaction)

    def read(self, estate_id, username):
        filename = _format_reaction_filename(estate_id, username)
        return self.db.read(filename)

    def read_by_estate(self, estate_id):
        user_reactions = self.db.read_glob(f"{estate_id}*")
        return list(map(_map_reaction, user_reactions))

    def read_all(self):
        records = self.db.read_all()
        return list(map(_map_reaction, records.items()))


def _write_text(filepath, content):
    filepath.write_text(content)
    pass


def _write_json(filepath, content):
    with open(filepath, "w") as f:
        json.dump(content, f)


def _read_text(filepath, default):
    return io.try_read_text(filepath, default)


def _read_json(filepath, default):
    return io.try_load_json(filepath, default)


class FileSystemDb:
    def __init__(self, db_path, is_json=False):
        assert db_path.is_dir(), "DB path must be a path to directory"
        self.db_path = db_path
        self.tmp_dir = db_path / ".tmp"
        self.tmp_dir.mkdir(exist_ok=True, parents=True)
        self.is_json = is_json

        if is_json:
            self._write_fn = _write_json
            self._read_fn = _read_json
        else:
            self._write_fn = _write_text
            self._read_fn = _read_text

    def write(self, filename, content):
        tmp_filepath = self.tmp_dir / filename

        self._write_fn(tmp_filepath, content)
        end_filepath = self.db_path / filename
        # assumed to be atomic
        shutil.move(tmp_filepath, end_filepath)

    def read(self, filename, default=None):
        filepath = self.db_path / filename
        return self._read_fn(filepath, default)

    def read_glob(self, glob):
        recs = ((f.stem, self.read(f.name)) for f in self.db_path.glob(glob))
        return [(f, r) for f, r in recs if r is not None]

    def _read_filepaths(self, sorted_=True):
        paths = (p for p in self.db_path.glob("*") if not p.is_dir())
        if sorted_:
            paths = sorted(paths)
        return paths

    def read_names(self, sorted_=True):
        paths = self._read_filepaths(sorted_=sorted_)
        names = (p.stem for p in paths)
        return list(names)

    def read_all(self):
        files = (f for f in self.db_path.glob("*") if not f.is_dir())
        return {f.stem: self.read(f.name) for f in files}

    #     def delete(self,filename):

    #         filename =pathlib.Path(filename)
    #         try:
    #             os.remove(filename)
    #         except FileNotFoundError:
    #             pass
    #         except Exception:
    #             logger.exception("Couldn't delete a file %s",filename)

    def pop(self):
        tmp_file = self.tmp_dir / str(uuid.uuid4())

        paths = self._read_filepaths()
        for p in paths:
            try:
                shutil.move(p, tmp_file)
                obj = self._read_fn(tmp_file, None)
                if obj is None:
                    continue  # this should not happen as the obj has been succesfully moved
                os.remove(tmp_file)
                return obj
            except FileNotFoundError:
                logger.debug("File not found while poping")

        return False
