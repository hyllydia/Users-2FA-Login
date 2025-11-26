# -*- coding: utf-8 -*-
# @Time    : 11/7/25
# @Author  : Yuling Hou
# @File    : Script6_API_login_2FA.py
# @Software: PyCharm
# -*- coding: utf-8 -*-
# @Time    : 9/29/25
# @Author  : Yuling Hou
# @File    : Script4_login_2FA.py
# @Software: PyCharm
# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import json
import os
from requests.auth import HTTPBasicAuth
from requests_toolbelt.adapters import source
from config_data import *
from Script1_delete_otp_files import remove_otp_file
import Script2_down_virtual_ifaces
import Script3_add_virtual_ifaces
import urllib3

urllib3.disable_warnings()

session = requests.Session()
session.verify = False


def login_user(ipstr, username):
    print(f"===******{username}---{ipstr}******===")
    new_source = source.SourceAddressAdapter(ipstr)
    session.mount('https://', new_source)
    body = {"domain": SSLVPNDOMAIN, "override": False, "snwl": True}
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-SNWL-API-Scope': 'extended',
        'X-SNWL-Timer': 'no-reset'
    }
    try:
        response = session.post(API_AUTH, auth=HTTPBasicAuth(username=username, password=PASSWORD),
                                data=json.dumps(body), headers=headers)
        if response.status_code == 200:
            print(f"{username} login success!")
            resp_data = response.json()
            auth_info = resp_data.get('status', {}).get('info', [{}])[0]
            bearer_token = auth_info.get('bearer_token')
            if not bearer_token:
                raise ValueError("Bearer token not found in response")

            session.headers.update({
                'Authorization': f'Bearer {bearer_token}',
                'X-SNWL-API-Scope': 'extended',
                'X-SNWL-Timer': 'no-reset',
                'Referer': f'https://{FIREWALL_IP}/',
                'Origin': f'https://{FIREWALL_IP}'
            })
            return True
    except requests.exceptions.RequestException as e:
        print(f"- LoginERROR - {e}")
    return False


def get_otp(username, timeout=30):
    """从上一级目录的data文件夹中获取OTP"""
    # 获取当前脚本所在目录（sslvpn_portal），然后跳到上一级目录，进入data文件夹
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)  # 上一级目录
    data_dir = os.path.join(parent_dir, 'data')  # 上一级目录下的data文件夹

    print(f"Looking for OTP files in: {data_dir}")

    start_time = time.time()
    while time.time() - start_time < timeout:
        if os.path.exists(data_dir):
            # 遍历data目录中的所有OTP文件
            for filename in os.listdir(data_dir):
                if filename.endswith('_otpcode.json'):
                    filepath = os.path.join(data_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            otp_dict = json.load(f)
                            if username in otp_dict:
                                otp_code = otp_dict[username]
                                print(f"Found OTP for {username}: {otp_code}")
                                return otp_code
                    except (json.JSONDecodeError, FileNotFoundError, Exception) as e:
                        print(f"Error reading {filename}: {e}")
                        continue

        # 如果没找到，等待后继续查找
        elapsed_time = time.time() - start_time
        print(f"OTP not found for {username}, waiting... ({int(elapsed_time)}s)")
        time.sleep(1)

    print(f"Timeout: No OTP found for {username} after {timeout} seconds")
    return None


def login_with_2FA(otp_code, username):
    try:
        otp_code = ''.join(c for c in otp_code if c.isalnum())
        response = session.post(API_OTP, json={'tfa': otp_code})
        if response.status_code == 200:
            print(f"{username}_2FA login success!")
            return True
        else:
            print(f"2FA verification failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"2FA request exception: {str(e)}")
        return False


if __name__ == "__main__":
    with open(MAPPING_FILE, 'r') as file:
        for line in file:
            username, vif, ip_addr = line.strip().split(',')
            if login_user(ip_addr, username):
                time.sleep(5)
                otp = get_otp(username)
                if otp:
                    print(f"Get {username} OTP Code: {otp}")
                    login_with_2FA(otp, username)
                else:
                    print(f"Timeout getting OTP for {username}")
                time.sleep(10)