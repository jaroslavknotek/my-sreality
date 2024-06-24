---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.14.5
  kernelspec:
    display_name: computer-vision
    language: python
    name: .venv
---

```python
%load_ext autoreload
%autoreload 2
```

```python
import numpy as np
import datetime
```

```python
import logging
logging.basicConfig()
logger = logging.getLogger('mysreality')
logger.setLevel(logging.INFO)

```

```python
import mysreality.estate_reader as er
```

```python
import pathlib

payloads_dir = pathlib.Path('/home/jry/data/baraky_hellno/payloads')
payloads_dir.mkdir(exist_ok=True,parents=True)

```

```python
from urllib.parse import urlparse

def _parse_estate_id(uri_text):
    return int(urlparse(uri_text).path.split('/')[-1])
```

```python
query_params = {
    'category_main_cb': '2',
    'object_kind_search': '1',
    'category_sub_cb': '37',
    'usable_area': '70|120',
    'estate_area': '250|10000000000',
    'no_shares': '1',
    'czk_price_summary_order2': '1000000|15000000',
    'no_auction': '1',
    'category_type_cb': '1'
}

df = er.read_estates(query_params,working_dir = payloads_dir)
```

```python
misleading_path = pathlib.Path('/home/jry/data/baraky_hellno/misleading.list')
with open(misleading_path) as f:
    misleading_uris = f.readlines()
    misleading = [_parse_estate_id(uri) for uri in misleading_uris]
df['misleading'] = False
df.loc[misleading]['misleading'] = True
```

```python
import mysreality.visualization as visu

df_close = df[df['commute_min'] < 90]
df_close = df_close[df_close['Stavba']!='Dřevostavba']
df_close[~df_close['misleading']]

app = visu.scatter(df_close)
app.run()
```

```python
def _norm(arr):
    arr_min = np.min(arr)
    arr_max = np.max(arr)
    return (arr -arr_min)/(arr_max-arr_min)

yy = _norm(df_close['commute_min'])
xx = _norm(df_close['price'])
cc = 1 - _norm(df_close['state_score'])
#cc =np.zeros_like(cc)

dists = np.sqrt(yy**2 + xx**2 + cc**2)
dist_idx = np.argsort(dists)
df_score_sorted = df_close.iloc[dist_idx]
```

```python
import pandas as pd
pd.set_option('display.max_colwidth', None)

candidates = df_score_sorted[['price','commute_min','Stav objektu','estate_id','link','state_score','Stav','closest_station_name','closest_station_km','Voda','Odpad']]
candidates = candidates.fillna("")
candidates.head(30)
```

```python
# todo kralupy
```

```python

```
