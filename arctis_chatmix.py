import asyncio
import logging
from argparse import ArgumentParser

from arctis_chatmix.arctis_chatmix_daemon import ArctisChatMixDaemon


if __name__ == '__main__':
    args = ArgumentParser()
    args.add_argument('-v', '--verbose', action='count', default=0)
    args = args.parse_args()

    logging.basicConfig(level=logging.CRITICAL, format='%(name)6s %(levelname)8s | %(message)s')

    daemon = ArctisChatMixDaemon(log_level=logging.DEBUG if args.verbose else logging.INFO)

    asyncio.run(daemon.start('1.1'))
