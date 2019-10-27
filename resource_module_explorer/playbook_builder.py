from collections import OrderedDict


class PlaybookBuilder(object):
    def __init__(self, host, os, resources, config=None):
        self._config = config
        self._host = host
        self._os = os
        self._resources = resources
        self._module = self._os + "_facts"


    def gfgf(self):
        playbook = [
            OrderedDict(
                {
                    "hosts": self._host,
                    "module_defaults": {
                        self._module: {
                            "gather_subset": "!all",
                            "gather_network_resources": self._resources,
                        }
                    },
                    "gather_facts": True,
                }
            )
        ]
        return playbook

    def gfpf(self):
        tasks = [
            OrderedDict(
                {
                    "name": "Use platform fact module",
                    self._module: {
                        "gather_subset": "!all",
                        "gather_network_resources": self._resources,
                    },
                }
            )
        ]
        playbook = [
            OrderedDict(
                {
                    "hosts": self._host,
                    "gather_facts": False,
                    "tasks": tasks,
                }
            )
        ]
        return playbook

    def ucrm(self):
        tasks = []
        for key, val in self._config.items():
            tasks.append(
                OrderedDict(
                    {
                        "name": "Configure {}".format(key),
                        "{}_{}".format(self._os, key): {"config": val},
                    }
                )
            )
        playbook = [
            OrderedDict(
                {
                    "hosts": self._host,
                    "gather_facts": False,
                    "tasks": tasks,
                }
            )
        ]
        return playbook

    def generate(self, playbook_name):
        playbook = getattr(self, playbook_name)()
        return playbook
