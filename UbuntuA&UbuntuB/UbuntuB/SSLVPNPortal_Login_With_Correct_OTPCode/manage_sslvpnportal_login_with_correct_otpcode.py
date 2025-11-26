# -*- coding: utf-8 -*-
# @Time    : 9/23/25
# @Author  : Yuling Hou
# @File    : manage_sslvpnportal_login.py

import subprocess
import os
import datetime
import sys
import time
import json
import requests
from requests.auth import HTTPBasicAuth
from requests_toolbelt.adapters import source
import urllib3
urllib3.disable_warnings()

# ===== 配置 =====
FIREWALL_IP = "172.185.0.1:4433"
FIREWALL_TYPE = "3800"
PASSWORD = "sonicwall2010"
SSLVPNDOMAIN = "LocalDomain"
BASE_IFACE = "ens192"
USER_COUNT = 1000
START_IP_A = 1
USER_PREFIX = "sslvpnLouser"
MAPPING_FILE = f"user_iface_{USER_COUNT}.txt"
OTP_FILE = f"./data/{FIREWALL_TYPE}_GreatWall_otpcode.json"

session = requests.Session()
session.verify = False

API_AUTH = f"https://{FIREWALL_IP}/api/sonicos/auth"
API_OTP = f"https://{FIREWALL_IP}/api/sonicos/one-time-password"

# ===== Step1: 删除旧虚拟网卡和 OTP 文件 =====
def delete_virtual_interfaces(base_iface, count):
    for i in range(1, 201):
        vif = f"{base_iface}:{i}"
        try:
            subprocess.run(['sudo', 'ifconfig', vif, 'down'], check=True)
            print(f"已关闭虚拟网卡 {vif}")
        except subprocess.CalledProcessError:
            pass  # 如果不存在就跳过

def remove_otp_file():
    if os.path.exists(OTP_FILE):
        try:
            os.remove(OTP_FILE)
            print(f"已删除旧 OTP 文件: {OTP_FILE}")
        except Exception as e:
            print(f"删除 OTP 文件失败: {e}")
    else:
        print("未发现 OTP 文件，无需清理")

# ===== Step2: 添加虚拟网卡 =====
def deal_ab(a,b):
    if b>255:
        b=1
        a+=1
    return a,b

def add_virtual_interfaces(base_iface, count, start_a=1):
    a = start_a
    b = 1
    mapping_list = []

    for i in range(1, count+1):
        a,b = deal_ab(a,b)
        vif = f"{base_iface}:{i}"
        ip_addr = f"172.185.{a}.{b}"
        try:
            subprocess.run(['sudo', 'ifconfig', vif, ip_addr, 'up'], check=True)
            print(f"已创建虚拟网卡 {vif} -> {ip_addr}")
        except subprocess.CalledProcessError as e:
            print(f"创建虚拟网卡失败: {vif} {ip_addr}, {e}")

        username = f"{USER_PREFIX}{i}"
        mapping_list.append((username, vif, ip_addr))
        b += 1

    # 写入映射文件
    with open(MAPPING_FILE, 'w') as f:
        for username, vif, ip_addr in mapping_list:
            f.write(f"{username},{vif},{ip_addr}\n")
    print(f"生成用户-虚拟网卡映射文件: {MAPPING_FILE}")
    return mapping_list

# ===== Step3: 登录操作 =====
def login_user(ipstr,username):
    print(f"===******{ipstr}******===")
    new_source = source.SourceAddressAdapter(ipstr)
    session.mount('https://', new_source)
    body = {"domain": SSLVPNDOMAIN, "override": False, "snwl": True}
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-SNWL-API-Scope': 'extended',  # 关键头
        'X-SNWL-Timer': 'no-reset'  # 关键头
}
    try:
        response = session.post(API_AUTH, auth=HTTPBasicAuth(username=username, password=PASSWORD), data=json.dumps(body),
                                headers=headers)
        if response.status_code == 200:
            print(f"{username} login sucess!")
            resp_data = response.json()
            #print(resp_data)

            auth_info = resp_data.get('status', {}).get('info', [{}])[0]
            bearer_token = auth_info.get('bearer_token')

            if not bearer_token:
                raise ValueError("响应中未找到bearer_token")

            # 更新会话头
            session.headers.update({
                'Authorization': f'Bearer {bearer_token}',
                'X-SNWL-API-Scope': 'extended',
                'X-SNWL-Timer': 'no-reset',
                'Referer': f'https://{FIREWALL_IP}/',
                'Origin': f'https://{FIREWALL_IP}'
            })

            return True
    except requests.exceptions.RequestException as e:
        print("- LoginERROR - Web service exception, msg = {}".format(e))

def get_otp(username, timeout=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if os.path.exists(OTP_FILE):
            with open(OTP_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        otp_dict = json.loads(line)
                        if username in otp_dict:
                            return otp_dict[username]
                    except json.JSONDecodeError:
                        continue
        time.sleep(0.5)
    return None

def login_with_2FA(otp_code,username):
    """第二次验证（使用保持的会话）"""
    try:
        # 确保OTP码是干净的
        otp_code = ''.join(c for c in otp_code if c.isalnum())

        # 使用已保持的会话发送请求
        response = session.post(
            API_OTP,
            json={'tfa': otp_code}
        )

        if response.status_code == 200:
            #print(response.json())
            print(f"{username}_2FA login success！")
            #print("响应:", response.json())
            return True
        else:
            print(f"2FA验证失败. 状态码: {response.status_code}")
            print("Error:", response.text)
            return False

    except Exception as e:
        print(f"2FA请求异常: {str(e)}")
        return False

def Step_1():
    # 1. 清理
    #remove_otp_file()
    delete_virtual_interfaces(BASE_IFACE, USER_COUNT)
    time.sleep(10)
def Step_2():
    # 2. 添加虚拟网卡 & 生成映射文件
    mapping_list = add_virtual_interfaces(BASE_IFACE, USER_COUNT)
    time.sleep(10)
    return mapping_list
# ===== 主流程 =====
if __name__ == "__main__":
    start_time = datetime.datetime.now()
    print(f"流程开始: {start_time}")
    remove_otp_file()
    Step_1()
    Step_2()

    # 3. 读取映射文件并执行登录操作
    with open(MAPPING_FILE, 'r') as file:
        for line in file:
            username, vif, ip_addr = line.strip().split(',')
            # Step1: user login action triggers that firewall send otp_code to smtp server
            login_user(ip_addr, username)
            time.sleep(5)  # 可调整并发节奏

            # Step2: 获取 OTP
            otp = get_otp(username)
            if otp:
                print(f"Get {username} OTP Code: {otp}")
                login_with_2FA(otp, username)
            else:
                print(f"获取 {username} 的OTP超时")
            time.sleep(10)

    end_time = datetime.datetime.now()
    print(f"流程结束: {end_time}")