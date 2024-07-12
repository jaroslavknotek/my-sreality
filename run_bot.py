import argparse
import logging

import mysreality.db as db
import mysreality.bot as bot
import mysreality.api as api
import mysreality.assets as assets
import pathlib

import logging


def setup_logging(args, main_logger_name=None):
    # external_loggers = ['httpx','apscheduler.scheduler','apscheduler.executors.default']
    # for logger_name in external_loggers:
    #     ext_logger = logging.getLogger(logger_name)
    #     ext_logger.setLevel(args.logLevel)

    logging.basicConfig(
        level=args.loglevel,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # this logger is always info
    if main_logger_name:
        logger = logging.getLogger("mysreality.telegram_bot")
        logger.setLevel(logging.INFO)


def setup_argparse():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-d",
        "--debug",
        help="Print lots of debugging statements",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.WARNING,
    )

    parser.add_argument("--token", help="Token to telegram bot", required=True)
    parser.add_argument("--root", help="Folder with estates data", required=True)
    parser.add_argument(
        "--interval",
        help="Number of seconds the bot waits before sending another message.",
        default=60,
        type=int,
    )

    parser.add_argument(
        "-v",
        "--verbose",
        help="Be verbose",
        action="store_const",
        dest="loglevel",
        const=logging.INFO,
    )

    return parser


def main():
    parser = setup_argparse()

    args = parser.parse_args()
    setup_logging(args, main_logger_name="mysreality.telegram_bot")

    root = pathlib.Path(args.root)
    reactions_dir = root / "user_reactions"
    reactions_db = db.ReactionsDb(reactions_dir)
    queue_dir = root / "queue"
    queue = db.DiscoveredQueue(queue_dir)

    reactions_map = assets.load_reactions_map()

    params = bot.Param(
        args.token,
        reactions_db,
        queue,
        reactions_map,
        interval=args.interval,
    )

    telegram_bot = bot.create_bot(params)
    telegram_bot.run_polling()


if __name__ == "__main__":
    main()
