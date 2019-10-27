from collections import OrderedDict
import queue

import asyncio
import aiohttp
import aiohttp_jinja2
import jinja2
import yaml

from .inventory_builder import InventoryBuilder
from .playbook_builder import PlaybookBuilder
from .playbook_runner import PlaybookRunner
from .event_filter import EventFilter



PLATFORMS = ["eos", "ios", "iosxr", "junos", "nxos", "vyos"]
RESOURCES = ["all", "interfaces", "l2_interfaces", "l3_interfaces", "vlans"]
DISABLED_RESOURCES = {"vyos": ["vlans"]}

yaml.add_representer(
    OrderedDict,
    lambda dumper, data: dumper.represent_mapping(
        "tag:yaml.org,2002:map", data.items()
    ),
)


class Server(object):
    def __init__(self):
        self.app = aiohttp.web.Application()
        self.app["websockets"] = []
        self.app.router.add_get("/", self.index)
        self.app.router.add_post("/render_inventory", self.render_inventory)
        self.app.router.add_post("/render_playbook", self.render_playbook)
        self.app.router.add_post("/run_playbook", self.run_playbook)
        self.app.router.add_get("/ws", self.websocket_handler)
        self.app.router.add_static('/static/', path='static', name='static')
        self.app.on_startup.append(self.start_background_tasks)
        self.eventq = queue.Queue()
        aiohttp_jinja2.setup(
            self.app, loader=jinja2.FileSystemLoader("./templates")
        )

    async def queue_watcher(self, appi):
        while True:
            await asyncio.sleep(1)
            while not self.eventq.empty():
                message = self.eventq.get()
                for webs in appi["websockets"]:
                    await webs.send_json(message)

    async def start_background_tasks(self, appi):
        appi.loop.create_task(self.queue_watcher(appi))

    @staticmethod
    async def index(request):
        context = {
            "disable_resources": DISABLED_RESOURCES,
            "platforms": PLATFORMS,
            "resources": RESOURCES,
        }
        response = aiohttp_jinja2.render_template(
            "index.html", request, context
        )
        return response

    @staticmethod
    async def websocket_handler(request):
        webs = aiohttp.web.WebSocketResponse()
        request.app["websockets"].append(webs)
        await webs.prepare(request)
        try:
            async for _msg in webs:
                pass
        finally:
            request.app["websockets"].remove(webs)
        print("websocket connection closed")
        return webs

    @staticmethod
    def generate_inventory(content):
        aib = InventoryBuilder(
            become=content.get("become", False),
            become_password=content.get("become_password"),
            host=content["host"],
            os=content["os"],
            password=content["password"],
            username=content["username"],
        )
        return aib.generate()

    @staticmethod
    def generate_playbook(content):
        apb = PlaybookBuilder(
            config=content.get("config"),
            host=content["host"],
            os=content["os"],
            resources=content["resources"],
        )
        return apb.generate(content["playbook_name"])

    async def render_inventory(self, request):
        content = await request.json()
        inventory = self.generate_inventory(content)
        for ptype in ["ansible_ssh_pass", "ansible_become_pass"]:
            if ptype in content:
                inventory[ptype] = "**********"
        return aiohttp.web.json_response({"inventory": yaml.dump(inventory)})

    async def render_playbook(self, request):
        content = await request.json()
        playbook = self.generate_playbook(content)
        return aiohttp.web.json_response({"playbook": yaml.dump(playbook)})

    async def run_playbook(self, request):
        content = await request.json()
        playbook = self.generate_playbook(content)
        inventory = self.generate_inventory(content)
        pbr = PlaybookRunner(inventory=inventory, playbook=playbook)
        events = await pbr.run(self.eventq)
        res = EventFilter(
            events=events, playbook_name=content["playbook_name"]
        ).filter()
        return aiohttp.web.json_response(res)

    def run(self):
        aiohttp.web.run_app(self.app)
