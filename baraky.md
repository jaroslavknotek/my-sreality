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
logger.setLevel(logging.DEBUG)
```

```python
import mysreality.estate_reader as er
```

```python
import pathlib

payloads_dir = pathlib.Path('/home/jry/data/baraky/payloads')
payloads_dir.mkdir(exist_ok=True,parents=True)

```

```python
def _intersect_ids(df,ids):
    existing_ids = set(df['estate_id'])
    return list(set(ids) & existing_ids)    
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

df_orig = er.read_estates(query_params,working_dir = payloads_dir)
df = df_orig
```

```python
class Pt:
    def __init__(self,x,y):
        self.x = x
        self.y = y
    
def is_left(a1, a2, p):
    a = Pt(*a1)
    b = Pt(*a2)
    c = Pt(*p)
    
    return (b.x - a.x)*(c.y - a.y) - (b.y - a.y)*(c.x - a.x) > 0

lovosice = 50.515121, 14.051127
havlickuv_brod = 49.607778, 15.580833 	

lat =np.array(df['gps_lat'].fillna(0))
lon = np.array(df['gps_lon'].fillna(0))
df['is_southwest'] = [is_left(lovosice,havlickuv_brod,(la,lo)) for la,lo in zip(lat,lon)]
```

```python
# co se s barakama da delat? spousta baraku ma divny dispozice

commute_estate = {
    4011673420:96,
    3763160396:67,
    3708253516:46,
    2543215948:28,
    4013721420:93,
    3501958476:108,
    802510156:100,
    1809651020:96,
    3553322316:79,
    3284686156:72,
    516121676:82,
    3543795020:77,
    2543215948:28,
    3895301452:98,
    4290012492:106,
    1542939980:87,
    812082508:108,
}

seen_state = {
    "good":{
        3284686156,
        "https://www.sreality.cz/detail/prodej/dum/rodinny/prevysov-prevysov-/1542939980#fullscreen=true&img=18", # potrebuje zateplit
        "https://www.sreality.cz/detail/prodej/dum/rodinny/slatina-slatina-/3553322316#fullscreen=false&img=0",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/dlouhopolsko-dlouhopolsko-fialova/2496157004#fullscreen=false&img=20",
    },
    "not_bad": {
        1286919500,
        4183041356,
        2944996684,
        "https://www.sreality.cz/detail/prodej/dum/rodinny/krupa-krupa-/2595956044#fullscreen=false&img=3", # plisen
        "https://www.sreality.cz/detail/prodej/dum/rodinny/zleby-zehuby-/1831249228#fullscreen=false&img=4",
    },
    "not_interested":{
        272377164,
        1143579980,
        3763160396,
        406590796,    
        "https://www.sreality.cz/detail/prodej/dum/rodinny/mecholupy-velka-cernoc-/1866405196",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/vojkovice-bukol-/3543795020#fullscreen=false&img=3",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/stasov--/129762636#fullscreen=false&img=8",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/onomysl-onomysl-/1524979020#fullscreen=false&img=29",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/bile-podoli-zaricany-/2215842892#fullscreen=false&img=16",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/kosik-kosik-/2868188492#fullscreen=false&img=5",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/strenice-strenice-/39081292#fullscreen=false&img=4",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/velenice-velenice-/2821297484#fullscreen=false&img=0",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/pnetluky-pnetluky-/2158785612#fullscreen=false&img=2",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/domousice-domousice-/3755828556#fullscreen=false&img=18",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/erpuzice-erpuzice-/3618395468",
    },
    "maybe":{
        "https://www.sreality.cz/detail/prodej/dum/rodinny/cervene-janovice-cervene-janovice-/3348370764#fullscreen=false&img=29",
        828929100,
        2543215948,
        2595956044,
        2630636876,
        1267193164,
        616133964,
        "https://www.sreality.cz/detail/prodej/dum/rodinny/pardubice-hostovice-/2403165516#fullscreen=false&img=4",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/vlkanec-pribyslavice-/218322252#fullscreen=false&img=21",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/horka-i-borek-/773739852#fullscreen=false&img=21",
    },
    "survivor":{
        "https://www.sreality.cz/detail/prodej/dum/rodinny/rozmital-pod-tremsinem-voltus-/802510156#img=3",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/konarovice-konarovice-na-labuti/828929100#fullscreen=true&img=0",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/zadni-treban-zadni-treban-pod-kvety/2543215948",
    },
    "scam": {
        'https://www.sreality.cz/detail/prodej/dum/rodinny/kralupy-nad-vltavou-kralupy-nad-vltavou-/3676112204',
        'https://www.sreality.cz/detail/prodej/dum/rodinny/rabyne-blazenice-/4278625612',
        'https://www.sreality.cz/detail/prodej/dum/rodinny/uhy-uhy-/1823786316',
        'https://www.sreality.cz/detail/prodej/dum/rodinny/kamenice-teptin-topolova/3455608140',
        'https://www.sreality.cz/detail/prodej/dum/rodinny/horni-bezdekov-horni-bezdekov-/3975288140#fullscreen=false&img=10',
        'https://www.sreality.cz/detail/prodej/dum/rodinny/kamenny-most-kamenny-most-/3903071564#fullscreen=false',
        'https://www.sreality.cz/detail/prodej/dum/rodinny/treboc-treboc-/1821774924#img=12',
        'https://www.sreality.cz/detail/prodej/dum/rodinny/vitice-hriby-/1585993036',
        'https://www.sreality.cz/detail/prodej/dum/chalupa/pavlikov-pavlikov-/337974348',
        'https://www.sreality.cz/detail/prodej/dum/rodinny/pavlikov-pavlikov-/3498579020',
        'https://www.sreality.cz/detail/prodej/dum/rodinny/brodce-brodce-rude-armady/3754353996#fullscreen=false&img=16'
    }
}

import mysreality.sreality as sreality

def parse_estate_ids(uris):
    return {sreality.parse_estate_id_from_uri(uri) for uri in uris}
def setup_state_seen(df,seen_state):
    df['state_seen'] = None
    for k,v in seen_state.items():
        ids = _intersect_ids(df,parse_estate_ids(v))
        df.loc[ids,'state_seen'] = k

setup_state_seen(df,seen_state)

commute_ids = _intersect_ids(df,commute_estate.keys())
df.loc[commute_ids,['commute_min']] = [ commute_estate[cid] for cid in commute_ids]
```

```python
import mysreality.visualization as visu

#df = df_orig
df = df[df['is_southwest']]
df = df[df['price'] < 4500000]
df = df[df['commute_min'] < 90]
df = df[df['Stavba']!='Dřevostavba']
df = df[df['state_score']>4]
df = df[df['state_seen'].isnull()]

app = visu.scatter(df)
app.run()
```

```python
import mysreality.visualization as visu

df_stribro = df_orig
df_stribro = df_stribro[df_stribro['closest_station_name'] == "Stříbro"]
df_stribro = df_stribro[df_stribro['Stavba']!='Dřevostavba']
df_stribro
app = visu.scatter(df_stribro)
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
