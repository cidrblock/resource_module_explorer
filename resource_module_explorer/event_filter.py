from collections import OrderedDict

class EventFilter(object):
    def __init__(self, events, playbook_name):
        self._events = events
        self._playbook_name = playbook_name

    def filter(self):
        if self._playbook_name in ["gfgf", "gfpf"]:
            oked = [
                event
                for event in self._events
                if '_facts' in event.get("event_data", {}).get("task_action", "")
                and event["event"] == "runner_on_ok"
            ]

            if oked:
                res = oked[0]["event_data"]["res"]["ansible_facts"][
                    "ansible_network_resources"
                ]
                return OrderedDict(sorted(res.items()))
            else:
                failed = [
                    event
                    for event in self._events
                    if event["event"] == "runner_on_failed"
                ]
                return {"events": failed}
        elif self._playbook_name in ["ucrm"]:
            res = []
            for event in self._events:
                if event["event"] == "runner_on_ok":
                    nevent = {event["event_data"]["task_action"]: {
                        "before": event['event_data']['res']['before'],
                        "after": event['event_data']['res'].get('after', None),
                        "commands": event['event_data']['res']['commands'],
                        "changed": event['event_data']['res']['changed'],
                        "status": "ok"
                    }}
                    res.append(nevent)
                if event['event'] == "runner_on_failed":
                    nevent = {event["event_data"]["task_action"]: {
                        "msg": event['event_data']['res']['msg'],
                        "status": "failed"
                    }}
                    res.append(nevent)
            return {"results": res}
