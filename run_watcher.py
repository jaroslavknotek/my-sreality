import mysreality.db as db
import mysreality.estate_reader as er
import mysreality.api as api
import mysreality.assets as assets
import mysreality.watcher as watcher
import pathlib
import time
import argparse
import logging


def filter_df(df):
    df = df[df["price"] < 4500000]
    is_near_external_station = (df["closest_station_km"] < 15) & (
        df["closest_station_name"] != "Praha"
    )
    is_near_prague = (df["closest_station_km"] < 30) & (
        df["closest_station_name"] == "Praha"
    )
    df = df[is_near_external_station | is_near_prague]
    df = df[df["Plocha pozemku"] > 500]
    df = df[(df["Stavba"] != "Dřevostavba") & (df["Stavba"] != "Montovaná")]
    df = df[df["state_score"] > 4]
    df = df[df["reaction"].isnull()]  # not previously seen

    return df


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

    parser.add_argument("--root", help="Folder with estates data", required=True)
    parser.add_argument(
        "--interval",
        help="Number of minutes between checking estates",
        default=30,
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
    setup_logging(args, main_logger_name="mysreality")

    root = pathlib.Path(args.root)
    reactions_dir = root / "user_reactions"
    reactions_db = db.ReactionsDb(reactions_dir)

    estates_data_path = root / "payloads"
    estate_reader = er.EstateReader(estates_data_path)
    estates_api = api.EstatesAPI(reactions_db, estate_reader)

    timestamp_path = root / "timestamp.txt"
    timestamper = db.TimestampPersitor(timestamp_path)

    queue_dir = root / "queue"
    queue = db.DiscoveredQueue(queue_dir)

    estates_watcher = watcher.EstateWatcher(
        estates_api,
        timestamper,
        queue,
        filter_fn=filter_df,
        interval_minutes=args.interval,
    )

    estates_watcher.sync()
    estates_watcher.watch()
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
