import asyncio
import logging
import pathlib
from collections import Counter

from mysreality.sreality import parse_estate_id_from_uri
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


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
        advert = params.watcher.pop()

        if advert:
            link, commute = advert["link"], advert["commute_min"]
            logger.debug(f"Trying {link}")
            buttons = get_reaction_keys(parse_estate_id_from_uri(link), params.reactions)
            base_message_text = create_message_text(link, commute, note="Commute [min]: ")

            await context.bot.send_message(chat_id=chat_id, text=base_message_text, reply_markup= buttons)
            logger.debug(f"Sent {link}")
            await asyncio.sleep(1)
    return send_links_cr

def create_message_text(link, commute, note=""):
    return f"{link}\n{note}{commute}"

def create_send_links(params):
    async def send_links(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat_id = update.message.chat_id
        await create_send_links_cr(params, chat_id)(context=context)
    return send_links

def create_button(params):
    async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        def get_reaction_counts(link_reactions):
            reaction_count_dict = {reaction: 0 for reaction in params.reactions.keys()}
            reaction_counter = Counter(link_reactions.values())
            reaction_count_dict.update(reaction_counter)
            return reaction_count_dict

        query = update.callback_query
        await query.answer()
        link, commute = query.message.text.split("\n")[:2]

        action, link_id = query.data.split("_")
        user = query.from_user.username
        params.estates_api.write_reaction(link, user, action)
        link_reactions = params.estates_api.read_reactions(link)

        reaction_counts = " ".join(
            f"| {params.reactions[reaction]} {count} |"
            for reaction, count in get_reaction_counts(link_reactions).items()
        )
        base_message_text = create_message_text(link, commute)
        await query.edit_message_text(text=f"{base_message_text}\n{reaction_counts}",
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
                watcher,

                ) -> None:
        self.bot_token = bot_token
        self.interval = interval
        self.estates_api = estates_api
        self.reactions = reactions
        cache_dir = pathlib.Path(cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)
        self.ts_path = cache_dir/"ts.txt"
        self.filter_fn = filter_fn
        self.watcher = watcher


def run_bot(params) -> None:
    application = Application.builder().token(params.bot_token).build()

    application.add_handler(CommandHandler("send_links", create_send_links(params)))
    application.add_handler(CommandHandler("auto", create_start_auto_messaging(params)))
    application.add_handler(CommandHandler("stop", stop_notify))
    application.add_handler(CallbackQueryHandler(create_button(params)))

    application.run_polling()
