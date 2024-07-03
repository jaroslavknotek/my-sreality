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
import pathlib
import numpy as np


root =pathlib.Path('/disk/knotek/baraky')
payloads_dir = root/'payloads'
db_path = root/'reactions.db'

from datetime import  datetime,timedelta
import mysreality.api as api

estates_api = api.EstatesAPI(db_path,payloads_dir)

#df = estates_api.read_latest()
```

```python
def filter_df(df):
    df = df[df["price"] < 4500000]
    df = df[df["commute_min"] < 90]
    df = df[df["Plocha pozemku"] > 500]
    df = df[(df["Stavba"]!="Dřevostavba") &  (df["Stavba"]!="Montovaná")]
    df = df[df["state_score"]>4]
    df = df[df["state_seen"].isnull()] # not previously seen

    return df

dff = filter_df(df)
print(len(dff))
dff
```

```python
dfx = df.loc[[812082508]]

def fn(df):
    df = df[df["price"] < 4500000]
    print(len(df))
    df = df[df["commute_min"] < 90]
    print(len(df))
    df = df[df["Plocha pozemku"] > 500]
    print(len(df))
    df = df[(df["Stavba"]!="Dřevostavba") &  (df["Stavba"]!="Montovaná")]
    print(len(df))
    df = df[df["state_score"]>4]
    print(len(df))
    df = df[df["state_seen"].isnull()] # not previously seen
    print(len(df))

    return df

fn(dfx)
```

```python
import mysreality.sreality as sreality

seen_state = {
    "top":{
    },
    "good":{
        3284686156,
        "https://www.sreality.cz/detail/prodej/dum/rodinny/prevysov-prevysov-/1542939980#fullscreen=true&img=18", # potrebuje zateplit
        "https://www.sreality.cz/detail/prodej/dum/rodinny/slatina-slatina-/3553322316#fullscreen=false&img=0",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/dlouhopolsko-dlouhopolsko-fialova/2496157004#fullscreen=false&img=20",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/vinare-vinice-/1547097420#fullscreen=false&img=5",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/mestec-kralove-novy-/2620195916#fullscreen=false&img=14",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/mestec-kralove-novy-/590685516#fullscreen=false&img=7",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/kozarovice-kozarovice-/734332236#fullscreen=false&img=5",
        1286919500,
        4183041356,
        2944996684,
        "https://www.sreality.cz/detail/prodej/dum/rodinny/krupa-krupa-/2595956044#fullscreen=false&img=3", # plisen
        "https://www.sreality.cz/detail/prodej/dum/rodinny/zleby-zehuby-/1831249228#fullscreen=false&img=4",
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
        "https://www.sreality.cz/detail/prodej/dum/rodinny/lhota-u-pribrame-lhota-u-pribrame-/1210271052#fullscreen=false&img=14",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/olesnice-olesnice-/39744844#fullscreen=false&img=6",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/hrochuv-tynec-sticany-/3000407628#fullscreen=false&img=0",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/knezice-knezice-/2153940300#fullscreen=false&img=9",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/umonin-brezova-/553125196#fullscreen=false&img=31",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/nezabudice--/2341823820#fullscreen=false&img=6",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/stribro-stribro-zadni/2148992332#fullscreen=false",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/stribro-stribro-premyslova/3125507404#fullscreen=false&img=1",
    },
    "survivor":{
        "https://www.sreality.cz/detail/prodej/dum/rodinny/klasterni-skalice-klasterni-skalice-/3169543244#fullscreen=false&img=22", # pecka
        "https://www.sreality.cz/detail/prodej/dum/rodinny/kluky-nova-lhota-/3696387404#fullscreen=false&img=19", # sasa: "nejvic peckovky", "da se tam zit".
        "https://www.sreality.cz/detail/prodej/dum/rodinny/rozmital-pod-tremsinem-voltus-/802510156#img=3",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/konarovice-konarovice-na-labuti/828929100#fullscreen=true&img=0",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/zadni-treban-zadni-treban-pod-kvety/2543215948",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/zbysov-klucke-chvalovice-/2820461900#fullscreen=false&img=13",
    },
    "nono":{
        272377164,
        1143579980,
        3763160396,
        406590796, 
        "https://www.sreality.cz/detail/prodej/dum/rodinny/chotesov-tynec-/2469098828#fullscreen=false&img=9",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/mesto-touskov--v-zahradkach/3247723852#fullscreen=false&img=19",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/libochovice-poplze-na-vrsku/2210673740#fullscreen=false&img=20",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/vrbicany-vrbicany-/821036364#fullscreen=false&img=29",
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
        "https://www.sreality.cz/detail/prodej/dum/rodinny/trpisty--/877163596#fullscreen=false",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/jince-jince-husova/3031188812#fullscreen=false&img=16",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/kozarovice-kozarovice-/2391729484#fullscreen=false&img=22",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/bratrinov-bratrinov-/2077967692#fullscreen=false&img=18",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/nyrany-nyrany-benesova-trida/2844063052",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/liban-psinice-/3086411084#fullscreen=false&img=4",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/ovcary-ovcary-u-rybnicku/516121676#fullscreen=false&img=16",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/kyskovice-kyskovice-/3908396364#fullscreen=false&img=0",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/dusniky--/1585661260#fullscreen=false&img=16",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/horni-kozolupy-slavice-/835667276#fullscreen=false&img=12",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/trpisty-svinomazy-/1315394892#fullscreen=true&img=24",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/plzen-cerveny-hradek-pod-skolou/3399574860#fullscreen=false&img=10",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/semtes-semtes-/3322967372#fullscreen=false&img=0",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/konarovice-konarovice-na-pruhone/2969175372#fullscreen=false&img=16",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/libkovice-pod-ripem--/2929796428#fullscreen=false&img=13",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/kutna-hora-karlov-hrncirska/2652349772#fullscreen=false&img=14",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/konstantinovy-lazne-okrouhle-hradiste-/2102154572#fullscreen=false&img=22",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/konstantinovy-lazne-bretislav-/417006924#fullscreen=false&img=22",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/kotovice-zaluzi-/1078469964",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/nyrany-doubrava-/2672321868#fullscreen=false&img=6",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/listany-lipno-/2675254604#fullscreen=false&img=16",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/krelovice-pakoslav-/33670476",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/oselin-oselin-/3009041484#fullscreen=false",
    },
    "scam": {
        "https://www.sreality.cz/detail/prodej/dum/rodinny/vodranty-vodranty-/1436640588#fullscreen=false&img=18",
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
        'https://www.sreality.cz/detail/prodej/dum/rodinny/brodce-brodce-rude-armady/3754353996#fullscreen=false&img=16',
        "https://www.sreality.cz/detail/prodej/dum/rodinny/cernovice-cernovice-/1593906508",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/cisovice--/549832524#fullscreen=false",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/trnova-trnova-/3385972044#fullscreen=false",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/kotovice-kotovice-/1763726668#fullscreen=false&img=12",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/cervene-pecky-opatovice-/1478481228",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/cervene-pecky-opatovice-/1951016268",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/maly-ujezd-jelenice-/1844299084#fullscreen=false&img=4",
        "https://www.sreality.cz/detail/prodej/dum/rodinny/krnany-trebsin-/4011673420",
    }
}

# test write
estates_api.db.deldb()
for k,v in seen_state.items():
    for estate_link in v:
        if isinstance(estate_link,int):
            estate_id = sreality.parse_estate_id_from_uri(estate_link)
            if estate_id in df.index:
                estate_row = df.loc[estate_id]
                estate_link = estate_row['link']
            else:
                continue
        reaction_data = {'jry':k,'bebe':k}
        
        estates_api.write_reaction(estate_link,'jarlando',k)
        estates_api.write_reaction(estate_link,'bepea',k)


# test read
for k,v in seen_state.items():
    for estate_link in v:
        if isinstance(estate_link,int):
            estate_id = sreality.parse_estate_id_from_uri(estate_link)
            if estate_id in df.index:
                estate_row = df.loc[estate_id]
                estate_link = estate_row['link']
            else:
                continue
            
        #print(estates_api.read_reactions(estate_link))
```
