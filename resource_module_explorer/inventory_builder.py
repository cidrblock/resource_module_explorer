class InventoryBuilder(object):
    def __init__(self, become, become_password, host, os, password, username):
        self._become = become
        self._become_password = become_password
        self._host = host
        self._os = os
        self._password = password
        self._username = username

    def generate(self):
        if self._os == "junos":
            conn = "netconf"
        else:
            conn = "network_cli"
        ivars = {
            "ansible_user": self._username,
            "ansible_password": self._password,
            "ansible_connection": conn,
            "ansible_network_os": self._os,
            "ansible_python_interpreter": "python",
        }
        if self._become:
            ivars.update(
                {
                    "ansible_become_pass": self._become_password,
                    "ansible_become": self._become,
                    "ansible_become_method": "enable",
                }
            )
        inventory = {"all": {"hosts": self._host, "vars": ivars}}
        return inventory
