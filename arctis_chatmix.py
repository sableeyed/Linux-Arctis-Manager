import asyncio
import logging
from argparse import ArgumentParser
import os
from typing import Literal

# Setup the notify logging
NOTIFY = 19  # Right before "INFO"
notify_enabled = os.system('which notify-send 1>/dev/null 2>&1') == 0


def logging_notify(self: logging.Logger, summary: str, message: str, urgency: Literal['low', 'normal', 'critical'] = 'normal', *args, **kwargs):
    if notify_enabled:
        args = ['--app-name="Arctis ChatMix"', f'--urgency={urgency}']
        os.system(f'notify-send {' '.join(args)} "{summary}" "{message.format(*args, **kwargs).replace('"', '\\"')}"')
    else:
        self._log(logging.INFO, f'NOTIFICATION: {summary} :: {message}', args, **kwargs)


logging.Logger.notify = logging_notify
# Notify logging end


if __name__ == '__main__':
    from arctis_chatmix.arctis_chatmix_daemon import ArctisChatMixDaemon

    args = ArgumentParser()
    args.add_argument('-v', '--verbose', action='count', default=0)
    args = args.parse_args()

    logging.basicConfig(level=logging.CRITICAL, format='%(name)6s %(levelname)8s | %(message)s')

    daemon = ArctisChatMixDaemon(log_level=logging.DEBUG if args.verbose else NOTIFY)

    asyncio.run(daemon.start('1.3.1'))
