import ansible_runner
from pprint import pprint
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
import asyncio

class AnsibleWrapper:
    def __init__(
        self,
        username,
        password,
        resources,
        host,
        os,
        playbook,
        become=False,
        become_password=None,
        data=None,
    ):
        self._tasks = []
        self._username = username
        self._password = password
        self._host = host
        self._os = os
        self._become = become
        self._become_password = become_password
        self._module = self._os + "_facts"
        self._playbook = None
        self._playbook_name = playbook
        self._resources = resources
        self._data = data
        self._eventq = None
        self._events = []

    # def gfpf(self):
    #     self._tasks = [
    #         OrderedDict(
    #             {
    #                 "name": "use platform fact module",
    #                 self._module: {
    #                     "gather_subset": "!all",
    #                     "gather_network_resources": self._resources,
    #                 },
    #             }
    #         )
    #     ]
    #     self._playbook = [
    #         OrderedDict(
    #             {
    #                 "hosts": self._host,
    #                 "gather_facts": False,
    #                 "tasks": self._tasks,
    #             }
    #         )
    #     ]
    #     return self._playbook

    # def gfgf(self):
    #     self._playbook = [
    #         OrderedDict(
    #             {
    #                 "hosts": self._host,
    #                 "module_defaults": {
    #                     self._module: {
    #                         "gather_subset": "!all",
    #                         "gather_network_resources": self._resources,
    #                     }
    #                 },
    #                 "gather_facts": True,
    #             }
    #         )
    #     ]
    #     return self._playbook

    # def ucrm(self):
    #     self._tasks = []
    #     for key, val in self._data.items():
    #         self._tasks.append(
    #             OrderedDict(
    #                 {
    #                     "name": "Configure {}".format(key),
    #                     "{}_{}".format(self._os, key): {"config": val},
    #                 }
    #             )
    #         )
    #     self._playbook = [
    #         OrderedDict(
    #             {
    #                 "hosts": self._host,
    #                 "gather_facts": False,
    #                 "tasks": self._tasks,
    #             }
    #         )
    #     ]
    #     return self._playbook

    # def generate_playbook(self):
    #     playbook = getattr(self, self._playbook_name)()
    #     return playbook

    # def generate_inventory(self):
    #     inventory = self._inventory()
    #     return inventory

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
                playbook=getattr(self, self._playbook_name)(),
                inventory=self._inventory(),
                json_mode=True,
                quiet=True,
                event_handler=self._event_handler,
            ),
        )
        # if self._playbook_name in ["gfgf", "gfpf"]:
        #     oked = [
        #         event
        #         for event in self._events
        #         if event.get("event_data", {}).get("task_action")
        #         in ["gather_facts", self._module]
        #         and event["event"] == "runner_on_ok"
        #     ]
        #     if oked:
        #         res = oked[0]["event_data"]["res"]["ansible_facts"][
        #             "ansible_network_resources"
        #         ]
        #         return OrderedDict(sorted(res.items()))
        #     else:
        #         failed = [
        #             event
        #             for event in self._events
        #             if event["event"] == "runner_on_failed"
        #         ]
        #         return {"events": failed}
        # elif self._playbook_name in ["ucrm"]:
        #     res = []
        #     for event in self._events:
        #         if event["event"] == "runner_on_ok":
        #             nevent = {event["event_data"]["task_action"]: {
        #                 "before": event['event_data']['res']['before'],
        #                 "after": event['event_data']['res'].get('after', None),
        #                 "commands": event['event_data']['res']['commands'],
        #                 "changed": event['event_data']['res']['changed'],
        #                 "status": "ok"
        #             }}
        #             res.append(nevent)
        #         if event['event'] == "runner_on_failed":
        #             nevent = {event["event_data"]["task_action"]: {
        #                 "msg": event['event_data']['res']['msg'],
        #                 "status": "failed"
        #             }}
        #             res.append(nevent)
        #     return {"results": res}

    # def _inventory(self):
    #     inventory = {
    #         "all": {
    #             "hosts": self._host,
    #             "vars": {
    #                 "ansible_user": self._username,
    #                 "ansible_password": self._password,
    #                 "ansible_become_pass": self._become_password,
    #                 "ansible_become": self._become,
    #                 "ansible_become_method": "enable",
    #                 "ansible_connection": "network_cli",
    #                 "ansible_network_os": self._os,
    #                 "ansible_python_interpreter": "python",
    #             },
    #         }
    #     }
    #     return inventory
