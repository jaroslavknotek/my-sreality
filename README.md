# my-sreality

Use [Sreality](sreality.cz) to find an export estates in desired locations.

## Motivation

The portal Sreality is great tool to search for some estate. However, it quickly becomes painful when you look for specifics such distance to your parents, distance to work or infrastructure (water, sewage, gas) as the portal does not support using such criteria for search. Even more cumbersome is to catalogue and compare your findings. Therefore I made a tool that queries sreality using broad criteria, stores the results, scores each record according to our needs and then plots/prints the results.


## Features

- Telegram watchdog sending estates that you can react on. Reactions are then stored within DB for further processing
- Periodic watcher that downloads new estates according to your criteria

## Instalation

It's not a package therefore clone the repo and install requirements:

```
git clone https://github.com/jaroslavknotek/my-sreality/
cd my-sreality
pip install -f requirements.txt
```

## Example

**Run Watcher**

```python
reactions_db = db.ReactionsDb('<path-where-telegram-reactions-are-stored>')
estate_reader = er.EstateReader('<path-to-raw-estates-storage>')
estates_api = api.EstatesAPI(reactions_db,estate_reader)

    
timestamper = db.TimestampPersitor('<path-to-wacher-metadata>')
queue = db.DiscoveredQueue('<path-to-watcher-discovery-queue>')

# example advanced filter allowing filtering on custom fields
def filter_df(df):
    df = df[(df['closest_station_km'] < 30) & (df['closest_station_name'] == 'Praha')]
    df = df[df["Plocha pozemku"] > 500]
    df = df[(df["Stavba"]!="Dřevostavba") &  (df["Stavba"]!="Montovaná")]
    df = df[df["reaction"].isnull()] # not previously seen

    return df

estates_watcher = watcher.EstateWatcher(
    estates_api,
    timestamper,
    queue,
    filter_fn = filter_df,
    interval_minutes = args.interval
)

estates_watcher.sync()
estates_watcher.watch()
```


**Run Bot**
Can be in a separate process to watcher
```python
reactions_db = db.ReactionsDb('<same-path-to-reactions>')
queue = db.DiscoveredQueue('<same-path-to-queue>')
   
params = bot.Param(
    BOT_TOKEN_TELEGRAM, # you need to getit from telegram Father bot
    reactions_db,
    queue,
    assets.load_reactions_map(),
)

telegram_bot = bot.create_bot(params)
telegram_bot.run_polling()
```
<!-- ### Notebook
See [baraky.md] which

- queries sreality according to input parameters
- finds the nearest city (given by config, see below)
- calculates commute time (based on manually inserted time as idos is infamously hard to work with)
- scores the results according to price, commute time and technical state
- prints/plots results
 -->


## Config

The folder assets has these files:

- estate_score_map.json - maps technical state of the estate to a number
- stations.json - a list of station that we picked to live nearby (as we wish to commute by train) based on [this](https://provoz.spravazeleznic.cz/PORTAL/Show.aspx?path=/Data/Mapy/linky_dalkove_dopravy.pdf)
- default_sreality_query.json - query that's used to construct query
- reactions.json - mapping between categorical score and it's icon in telegram


# Endnote

- This readme is by no means a documentations. There is none so open the notebook and try for yourself or create an issue. 
- Given obscure security of sreality, this may stop working at any moment.







