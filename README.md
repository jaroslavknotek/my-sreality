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

### Script

Setup API:
```python
estates_api = api.EstatesAPI('<path to db>',"<payloads_dir>")
```

Setup watcher and wait till it syncs:
```python

# filter is provided in the form of a function that reads dataset
def filter_df(df):
    df = df[df["price"] < 4500000]
    df = df[df["commute_min"] < 90]
    df = df[df["Plocha pozemku"] > 500]
    df = df[(df["Stavba"]!="Dřevostavba") &  (df["Stavba"]!="Montovaná")]
    df = df[df["state_score"]>4]
    df = df[df["state_seen"].isnull()] # not previously seen

    return df

estates_watcher = api.EstateWatcher(
    estates_api,
    filter_fn = filter_df,
)
estates_watcher.sync()
```

Create bot:
```python
bot_token = "<TOKEN from telegram>"
params = bot.Param(
    bot_token,
    estates_api,
    estates_watcher
)
telegram_bot = bot.create_bot(params)
```

Run watcher + telegram bot:
```python
estates_watcher.watch()
telegram_bot.run_polling()
```

### Notebook
See [baraky.md] which

- queries sreality according to input parameters
- finds the nearest city (given by config, see below)
- calculates commute time (based on manually inserted time as idos is infamously hard to work with)
- scores the results according to price, commute time and technical state
- prints/plots results



## Config

The folder assets has these files:

- estate_score_map.json - maps technical state of the estate to a number
- stations.json - a list of station that we picked to live nearby (as we wish to commute by train)
- default_sreality_query.json - query that's used to construct query
- reactions.json - mapping between categorical score and it's icon in telegram


# Endnote

- This readme is by no means a documentations. There is none so open the notebook and try for yourself or create an issue. 
- Given obscure security of sreality, this may stop working at any moment.







