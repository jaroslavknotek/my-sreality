import os

from bot import Param, run_bot
from dotenv import load_dotenv
from mysreality.api import EstatesAPI, EstateWatcher
from mysreality.assets import load_reactions_map

load_dotenv()

bot_token = os.getenv("BOT_TOKEN")
db_path = "/tmp/data.db"
data_dir = "/tmp/payloads"
cache_dir = "/tmp/cache"
interval = 10


def filter_fn(df):
    df = df[df["price"] < 4_500_000]
    df = df[df["commute_min"] < 90]
    df = df[df["Plocha pozemku"] > 500]
    df = df[(df["Stavba"]!="Dřevostavba") &  (df["Stavba"]!="Montovaná")]
    df = df[df["state_score"]>4]
    df = df[df["state_seen"].isnull()] # for migration purposes
    return df

estates_api = EstatesAPI(db_path,data_dir)

watcher = EstateWatcher(
    estates_api,
    filter_fn=filter_fn,
    download_images=False,
)
watcher.watch()

params = Param(bot_token=bot_token,
                interval=interval,
                estates_api=estates_api,
                reactions=load_reactions_map(),
                cache_dir=cache_dir,
                filter_fn =filter_fn,
                watcher = watcher,
                )

run_bot(params)
