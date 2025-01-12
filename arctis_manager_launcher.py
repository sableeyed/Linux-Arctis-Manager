import asyncio
import os

from dbus_next import Message, MessageType
from dbus_next.aio import MessageBus

# Desktop application to summon the daemon's windows
# Specially designed for non-system tray desktop environments like GNOME


async def main():
    bus = await MessageBus().connect()
    message = Message(
        destination='name.giacomofurlan.ArctisManager',
        path='/name/giacomofurlan/ArctisManager',
        interface='name.giacomofurlan.ArctisManager',
        member='ShowSettings',
    )

    response = await bus.call(message)
    if response.message_type == MessageType.ERROR:
        args = ['--app-name="Arctis Manager"', '--urgency=normal', '--expire-time=5000']
        os.system(f'notify-send {' '.join(args)
                                 } "Arctis Manager" "Arctis Manager service is not available. Please connect the device first and try opening the app again."')

if __name__ == '__main__':
    asyncio.run(main())
