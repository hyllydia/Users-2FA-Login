# -*- coding: utf-8 -*-
# @Time    : 9/29/25
# @Author  : Yuling Hou
# @File    : Script3_add_virtual_ifaces.py
# @Software: PyCharm
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
from config_data import BASE_IFACE, USER_COUNT, USER_PREFIX, START_IP_A, MAPPING_FILE

def deal_ab(a, b):
    if b > 255:
        b = 1
        a += 1
    return a, b

def add_virtual_interfaces(base_iface, count, start_a=1):
    a = start_a
    b = 1
    mapping_list = []

    for i in range(1, count+1):
        a, b = deal_ab(a, b)
        vif = f"{base_iface}:{i}"
        ip_addr = f"172.185.{a}.{b}"
        try:
            subprocess.run(['sudo', 'ifconfig', vif, ip_addr, 'up'], check=True)
            print(f"Successfully created virtual interface {vif} -> {ip_addr}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to create virtual interface: {vif} {ip_addr}, {e}")

        username = f"{USER_PREFIX}{i}"
        mapping_list.append((username, vif, ip_addr))
        b += 1

    with open(MAPPING_FILE, 'w') as f:
        for username, vif, ip_addr in mapping_list:
            f.write(f"{username},{vif},{ip_addr}\n")

    print(f"Generated user-virtual interface mapping file: {MAPPING_FILE}")
    return mapping_list

if __name__ == "__main__":
    add_virtual_interfaces(BASE_IFACE, USER_COUNT, START_IP_A)
