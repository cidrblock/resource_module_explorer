import ansible_runner
from concurrent.futures import ThreadPoolExecutor
import asyncio

class PlaybookRunner:
    def __init__(self, inventory, playbook):
        self._inventory = inventory
        self._playbook = playbook
        self._eventq = None
        self._events = []

    def _event_handler(self, event):
        self._eventq.put({"event": event})
        self._events.append(event)

    async def run(self, eventq):
        """ run
        """
        self._eventq = eventq
        executor = ThreadPoolExecutor(max_workers=1)
        loop = asyncio.get_event_loop()

        await loop.run_in_executor(
            executor,
            lambda: ansible_runner.run(
                playbook=self._playbook,
                inventory=self._inventory,
                json_mode=True,
                quiet=True,
                event_handler=self._event_handler,
            ),
        )
        return self._events
