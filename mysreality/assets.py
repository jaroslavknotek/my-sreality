import pathlib
import mysreality.io as io

asset_root = pathlib.Path(f"{__file__}").parent.parent/'assets'

def read_default_sreality_query():
    return io.load_json(asset_root/'default_sreality_query.json')

def load_estate_score_map():
    return io.load_json(asset_root/'estate_score_map.json')

def load_stations():
    return io.load_json(asset_root/'stations.json')

def load_reactions_map():
    return io.load_json(asset_root/'reactions_map.json')