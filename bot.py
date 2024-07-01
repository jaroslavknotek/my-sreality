import logging
import os
import pathlib
from datetime import datetime, timedelta

from mysreality import api
from mysreality.assets import load_reactions_map
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def write_ts(params, ts):
    with open(params.ts_path, "w") as f:
        f.write(ts.timestamp())

def get_latest_ts(params):
    if not pathlib.Path(params.ts_path).exists():
        return datetime.fromtimestamp(1545730073)
    with open(params.ts_path) as f:
        return datetime.fromtimestamp(int(f.read()))

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
        buffer = 5
        df = params.estates_api.read_latest(now - timedelta(seconds=params.interval) - buffer)
        df = params.filter_fn(df)
        links = df["link"]
        for link in links:
            #TODO: filter links with reactions
            await context.bot.send_message(chat_id=chat_id, text=link, reply_markup=get_reaction_keys(link.strip(), params.reactions) )
    return send_links_cr


def create_send_links():
    async def send_links(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat_id = update.message.chat_id
        await create_send_links_cr(chat_id)(context=context)
    return send_links

def create_button(params):
    async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()

        action, link = query.data.split("_")
        user = query.from_user.username
        params.estates_api.write_reaction(link, user, action)
        link_reactions = params.estates_api.read_reactions(link)
        reaction_counts = " ".join([f"| {params.reactions[reaction]} {len(users)} |"
                                    for reaction, users in link_reactions.items()])
        await query.edit_message_text(text=f"{link}\n{reaction_counts}", reply_markup=get_reaction_keys(link, params.reactions))
    return button

class Param:
    def __init__(self,
                bot_token,
                interval,
                estate_api,
                reactions,
                cache_dir,
                filter_fn,

                ) -> None:
        self.bot_token = bot_token
        self.interval = interval
        self.estate_api = estate_api
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


    def filter_df(df):
        df = df[df['price'] < 4500000]
        df = df[df['commute_min'] < 90]
        df = df[df['Plocha pozemku'] > 500]
        df = df[(df['Stavba']!='Dřevostavba') &  (df['Stavba']!='Montovaná')]
        df = df[df['state_score']>4]
        df = df[df['state_seen'].isnull()] # not previously seen
        #df = df[df['is_southwest']]
        return df

    estates_api = api.EstatesAPI(db_path,data_dir)
    long_ago = datetime.now() - timedelta(weeks=24000)
    estates_api.read_latest(long_ago)
    params = Param(bot_token=bot_token,
                   interval=3600,
                   estate_api=estates_api,
                   reactions=load_reactions_map(),
                   cache_dir=cache_dir,
                   filter_fn =filter_df
                   )
    run_bot(params)
