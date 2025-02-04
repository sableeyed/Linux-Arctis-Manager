import asyncio


class Waiter:
    def __init__(self):
        self._event = asyncio.Event()
    
    def set(self):
        self._event.set()
    
    def __await__(self):
        return self._event.wait().__await__()
