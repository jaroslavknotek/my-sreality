import logging
import os
import pathlib
from datetime import datetime, timedelta
from collections import Counter

import pandas as pd
import asyncio
from mysreality import api
from mysreality.assets import load_reactions_map
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes
from mysreality.sreality import parse_estate_id_from_uri


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def write_ts(params, ts):
    with open(params.ts_path, "w") as f:
        f.write(str(ts.timestamp()))

def get_latest_ts(params):
    default_ts = datetime.fromtimestamp(1545730073)
    ts_path = pathlib.Path(params.ts_path)
    if not ts_path.exists():
        return default_ts
    try:
        with ts_path.open() as f:
            timestamp = float(f.read().strip())
            return datetime.fromtimestamp(timestamp)
    except (ValueError, OSError) as e:
        # Handle error: log it, raise an exception, or return a default value
        logger.info(f"Error reading timestamp: {e}")
        return default_ts

def get_reaction_keys(link, reactions):
    keyboard = [
            [InlineKeyboardButton(reactions[reaction], callback_data=f"{reaction}_{link}")
             for reaction in reactions.keys()]
        ]
    return InlineKeyboardMarkup(keyboard)

def create_start_auto_messaging(params):
    async def start_auto_messaging(update, context):
        chat_id = update.message.chat_id
        await context.bot.send_message(chat_id=chat_id, text="Starting automatic messages!")
        context.job_queue.run_repeating(create_send_links_cr(params, chat_id),
                                        params.interval,
                                        chat_id=chat_id, name=str(chat_id))
    return start_auto_messaging

async def stop_notify(update, context):
    chat_id = update.message.chat_id
    await context.bot.send_message(chat_id=chat_id, text="Stopping automatic messages!")
    jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    if len(jobs):
        jobs[0].schedule_removal()

def create_send_links_cr(params, chat_id):
    async def send_links_cr(context):
        now = datetime.now()
        # FIXME buffer
        buffer = 5
        # delta = timedelta(seconds=params.interval)
        df = pd.read_csv("./estates_20240701.csv")
        # df = params.estates_api.read_latest(get_latest_ts(params), images=False)
        df = params.filter_fn(df)
        df = df.head()
        links = df["link"]
        links = links.tolist()  # FIXME
        
        # links = ["https://slovnik.seznam.cz/preklad/anglicky_cesky/purr",
        #         "https://slovnik.seznam.cz/preklad/anglicky_cesky/slur",
        #         "https://slovnik.seznam.cz/preklad/anglicky_cesky/murr",
        #         ] * 3
        
        for link in links:
            #TODO: filter links with reactions
            logger.info(f"Trying {link}")
            buttons = get_reaction_keys(parse_estate_id_from_uri(link), params.reactions)
            await context.bot.send_message(chat_id=chat_id, text=link.strip(), reply_markup= buttons)
            logger.info(f"Sent {link}")
            await asyncio.sleep(1)
        write_ts(params, now)
    return send_links_cr


def create_send_links(params):
    async def send_links(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat_id = update.message.chat_id
        await create_send_links_cr(params, chat_id)(context=context)
    return send_links

def create_button(params):
    async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        
        query = update.callback_query
        await query.answer()
        link = query.message.text.split("\n")[0]
        print("Parsed link:", repr(link)) 
        action, link_id = query.data.split("_")
        user = query.from_user.username
        params.estates_api.write_reaction(link, user, action)
        link_reactions = params.estates_api.read_reactions(link)

        reaction_count_dict = {reaction: 0 for reaction in params.reactions.keys()}
        reaction_counter = Counter(link_reactions.values())
        reaction_count_dict.update(reaction_counter)

        reaction_counts = " ".join(
            f"| {params.reactions[reaction]} {count} |" 
            for reaction, count in reaction_count_dict.items()
        )       
        await query.edit_message_text(text=f"{link}\n{reaction_counts}",
                                      reply_markup=get_reaction_keys(link_id, params.reactions))
    return button

class Param:
    def __init__(self,
                bot_token,
                interval,
                estates_api,
                reactions,
                cache_dir,
                filter_fn,

                ) -> None:
        self.bot_token = bot_token
        self.interval = interval
        self.estates_api = estates_api
        self.reactions = reactions
        cache_dir = pathlib.Path(cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)
        self.ts_path = cache_dir/"ts.txt"
        self.filter_fn = filter_fn


def run_bot(params) -> None:
    application = Application.builder().token(params.bot_token).build()

    application.add_handler(CommandHandler("send_links", create_send_links(params)))

    application.add_handler(CommandHandler("auto", create_start_auto_messaging(params)))
    application.add_handler(CommandHandler("stop", stop_notify))

    # Handle button clicks
    application.add_handler(CallbackQueryHandler(create_button(params)))

    # Start the Bot
    application.run_polling()

#TODO: add commute_min

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    bot_token = os.getenv("BOT_TOKEN")
    db_path = "/tmp/data.db"
    data_dir = "/tmp/payloads"
    cache_dir = "/tmp/cache"
    interval = 10


    def filter_df(df):
        df = df[df["price"] < 4500000]
        df = df[df["commute_min"] < 90]
        df = df[df["Plocha pozemku"] > 500]
        df = df[(df["Stavba"]!="Dřevostavba") &  (df["Stavba"]!="Montovaná")]
        df = df[df["state_score"]>4]
        df = df[df["state_seen"].isnull()] # not previously seen
        #df = df[df['is_southwest']]
        return df

    
    # watcher = api.EstateWatcher(
    #     estates_api,
    #     filter_fn
    # )
    # estates_api = api.EstatesAPI(db_path,data_dir)
    # watcher.watch() 
    
    
    long_ago = datetime.now() - timedelta(weeks=24000)
    # estates_api.read_latest(long_ago, images=False)
    params = Param(bot_token=bot_token,
                #    interval=3600,
                   interval=interval,
                   estates_api=estates_api,
                   reactions=load_reactions_map(),
                   cache_dir=cache_dir,
                   filter_fn =filter_df
                   )
    
    run_bot(params)
