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

def filter_df(df):
    df = df[df["price"] < 4500000]
    is_near_external_station = (df['closest_station_km'] < 15) & (df['closest_station_name'] != 'Praha')
    is_near_prague = (df['closest_station_km'] < 30) & (df['closest_station_name'] == 'Praha')
    df = df[is_near_external_station | is_near_prague]
    df = df[df["Plocha pozemku"] > 500]
    df = df[(df["Stavba"]!="Dřevostavba") &  (df["Stavba"]!="Montovaná")]
    df = df[df["state_score"]>4]
    df = df[df["reaction"].isnull()] # not previously seen

    return df

len(filter_df(df))
```
