from resource_module_explorer.server import Server

RESOURCES = [
    "all",
    "interfaces",
    "l2_interfaces",
    "l3_interfaces",
    "lacp_interfaces",
    "lag_interfaces",
    "lldp_global",
    "telemetry",
    "vlans",
]

SETTINGS = {
    "platforms": ["ios", "iosxr", "eos", "junos", "nxos", "vyos"],
    "resources": {
        "eos": [x for x in RESOURCES if x not in ['telemetry']],
        "ios": [x for x in RESOURCES if x not in ['telemetry']],
        "iosxr": [x for x in RESOURCES if x not in ['telemetry']],
        "junos": [x for x in RESOURCES if x not in ['telemetry']],
        "nxos": [x for x in RESOURCES if x not in []],
        "vyos": [x for x in RESOURCES if x not in ['telemetry', 'vlans']],
    },
}

if __name__ == "__main__":
    Server(settings=SETTINGS).run(host="0.0.0.0", port=8080)
