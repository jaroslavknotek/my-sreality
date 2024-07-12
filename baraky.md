---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.14.6
  kernelspec:
    display_name: torch_cv
    language: python
    name: torch_cv
---

```python
%load_ext autoreload
%autoreload 2
```

```python
import logging
logging.basicConfig()
logger = logging.getLogger('mysreality')
logger.setLevel(logging.INFO)

```

```python
import mysreality.estate_reader as er
import pathlib
import numpy as np

from datetime import  datetime,timedelta
import mysreality.api as api
import mysreality.db as db

root =pathlib.Path('/disk/knotek/baraky')
estates_data_path = root/'payloads'
reactions_dir = root/'user_reactions'

estate_reader = er.EstateReader(estates_data_path)
rdb = db.ReactionsDb(reactions_dir)
estates_api = api.EstatesAPI(rdb,estate_reader)
df = estates_api.read()
```

```python
import mysreality.visualization as visu

def is_cheap(df):
    filter_ = df["price"] < 4500000
    is_near_external_station = (df['closest_station_km'] < 15) & (df['closest_station_name'] != 'Praha')
    is_near_prague = (df['closest_station_km'] < 30) & (df['closest_station_name'] == 'Praha')
    filter_ &= is_near_external_station | is_near_prague
    filter_ &= df["Plocha pozemku"] > 500
    filter_ &= (df["Stavba"]!="Dřevostavba") &  (df["Stavba"]!="Montovaná")
    filter_ &= df["state_score"]>4
    return filter_

def is_close(df):
    filter_ = df["price"] < 9_000_000
    filter_ &= df['distance_to_base_km'] < 15
    return filter_
```

```python
import pandas as pd
pd.set_option("max_colwidth", None)

def final_filter(df):
    df['is_cheap'] = is_cheap(df)
    df['is_close'] = is_close(df)
    df = df[(df['is_cheap']) | (df['is_close'])]
    return df[df['reaction'].isnull()]

final_filter(df)[["Celková cena","price", "link","commute_min"]]
```

```python
import geopy
import mysreality.assets as assets

stations = assets.load_stations()
praha_gps = stations['Praha']['gps']

{
    k:geopy.distance.geodesic(praha_gps,v['gps']).km 
    for k,v in stations.items()
}
```
