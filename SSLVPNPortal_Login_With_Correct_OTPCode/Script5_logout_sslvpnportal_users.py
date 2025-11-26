# -*- coding: utf-8 -*-
# @Time    : 9/29/25
# @Author  : Yuling Hou
# @File    : Script5_logout_sslvpnportal_users.py
# @Software: PyCharm
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from requests.auth import HTTPBasicAuth
from config_data import WEBGUI_IP, ADMIN, PASSWD, MAPPING_FILE
import urllib3
urllib3.disable_warnings()

session = requests.Session()
session.verify = False

API_AUTH = f"https://{WEBGUI_IP}/api/sonicos/auth"
API_SESSIONS = f"https://{WEBGUI_IP}/api/sonicos/user/sessions"

def get_ips_from_mapping(mapping_file):
    ips = []
    with open(mapping_file, "r") as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) == 3:
                _, _, ip = parts
                ips.append(ip)
    return ips

def admin_login():
    """Admin login to get Bearer Token"""
    body = {"override": False, "domain": "LocalDomain", "snwl": True}
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    resp = session.post(API_AUTH,
                        auth=HTTPBasicAuth(ADMIN, PASSWD),
                        json=body,
                        headers=headers)

    if resp.status_code == 200:
        try:
            auth_info = resp.json().get('status', {}).get('info', [{}])[0]
            token = auth_info.get('bearer_token')
            if token:
                session.headers.update({
                    "Authorization": f"Bearer {token}",
                    "X-SNWL-API-Scope": "extended"
                })
                print("Admin login successful!")
                return True
        except Exception as e:
            print("Error parsing token:", e)
    print("Admin login failed:", resp.status_code, resp.text)
    return False

def logout_users(ips):
    for ip in ips:
        payload = {"killusers": [{"ip": ip}]}
        print(f"****** delete user {ip} ******")
        resp = session.delete(API_SESSIONS, json=payload)
        print("Status:", resp.status_code)
        print("Response:", resp.text)

if __name__ == "__main__":
    if admin_login():
        ips = get_ips_from_mapping(MAPPING_FILE)
        print(f"Read {len(ips)} IPs from {MAPPING_FILE}, preparing to log out...")
        logout_users(ips)
