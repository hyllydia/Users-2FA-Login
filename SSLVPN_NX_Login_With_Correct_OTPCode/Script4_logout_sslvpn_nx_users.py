# -*- coding: utf-8 -*-
# @Time    : 10/21/25
# @Author  : Yuling Hou
# @File    : logout_sslvpn_nx_users.py
# @Software: PyCharm
import requests
from requests.auth import HTTPBasicAuth
from nx_data import WEBGUI_IP, ADMIN, PASSWD, MAPPING_FILE
import urllib3
import os

urllib3.disable_warnings()

session = requests.Session()
session.verify = False


def admin_login():
    body = {"override": True}
    resp = session.post(f"https://{WEBGUI_IP}/api/sonicos/auth",
                        auth=HTTPBasicAuth(ADMIN, PASSWD), json=body,
                        headers={'Accept': 'application/json', 'Content-Type': 'application/json'})

    if resp.status_code == 200:
        #token = resp.json()['status']['info'][0]['bearer_token']
        #session.headers.update({"Authorization": f"Bearer {token}", "X-SNWL-API-Scope": "extended"})
        return True
    return False


def logout_users_from_mapping():
    if not os.path.exists(MAPPING_FILE):
        print(f"Mapping file not found: {MAPPING_FILE}")
        return

    ips = []
    with open(MAPPING_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split(',')
            if len(parts) >= 2:
                username = parts[0]
                ip = parts[1]
                if ip != 'pending':
                    ips.append((username, ip))

    print(f"Found {len(ips)} users in {MAPPING_FILE}")

    for username, ip in ips:
        api_url = f"https://{WEBGUI_IP}/api/sonicos/ssl-vpn/logout/{ip}"
        resp = session.post(api_url)
        status = "Success" if resp.status_code == 200 else "Failed"
        print(f"Logout {username} ({ip}): {status}")


if __name__ == "__main__":
    admin_login()
    logout_users_from_mapping()
