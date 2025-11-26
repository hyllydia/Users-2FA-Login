# -*- coding: utf-8 -*-
# @Time    : 9/29/25
# @Author  : Yuling Hou
# @File    : Script2_down_virtual_ifaces.py
# @Software: PyCharm
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import re
from config_data import BASE_IFACE

def get_virtual_interfaces(base_iface):
    result = subprocess.run(["ifconfig"], capture_output=True, text=True)
    if result.returncode != 0:
        print("Failed to get network interface information:", result.stderr)
        return []

    interfaces = []
    for line in result.stdout.splitlines():
        m = re.match(rf"^({base_iface}:\d+)", line.strip())
        if m:
            interfaces.append(m.group(1))
    return interfaces

def shutdown_virtual_interfaces(base_iface):
    vifs = get_virtual_interfaces(base_iface)
    print(f"Found {len(vifs)} virtual interfaces: {vifs}")
    for vif in vifs:
        try:
            subprocess.run(['sudo', 'ifconfig', vif, 'down'], check=True)
            print(f"Virtual interface {vif} has been shut down")
        except subprocess.CalledProcessError:
            print(f"{vif} does not exist or cannot be shut down")

if __name__ == "__main__":
    shutdown_virtual_interfaces(BASE_IFACE)
