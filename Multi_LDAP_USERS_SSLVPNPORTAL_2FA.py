# -*- coding: utf-8 -*-
# @Time    : 9/22/25
# @Author  : Yuling Hou
# @File    : Multi_LDAP_USERS_SSLVPNPORTAL_2FA.py
# @Software: PyCharm
#coding:utf-8
#1、requests库
#2、sys.argv[]用来接收另一个python文件传递过来的参数；os.system("python 1.py {} {}".format(a,b))    a=sys.argv[1]   b=sys.argv[2]
#3、requests_toolbelt.adapters 用来设置虚拟IP，需要用不同的ip从同一个出口出去
import requests
from requests.auth import HTTPBasicAuth
from requests_toolbelt.adapters import source
import json
import sys
import os
import urllib3
import time
urllib3.disable_warnings()

FIREWALL_IP = "172.185.0.2:4433"
API_AUTH = f"https://{FIREWALL_IP}/api/sonicos/auth"
API_OTP = f"https://{FIREWALL_IP}/api/sonicos/one-time-password"
FIREWALL_TYPE = "2800"
PASSWORD = "hyllydia@2020"
SSLVPNDOMAIN = "LocalDomain"
# 会话保持
session = requests.Session()
session.verify = False
#OTP_FILE = "./data/5700_GreatWall_otpcode.json"  # 与服务器相同的文件路径
OTP_FILE = "./data/"+ FIREWALL_TYPE +"_GreatWall_otpcode.json"

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
            print(resp_data)

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

def login_2FA(otp_code):
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
            print(response.json())
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

def get_otp(username, timeout=10):
    """等待并获取OTP（改进版，支持逐行查找）"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            if os.path.exists(OTP_FILE):
                with open(OTP_FILE, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()  # 去除换行符
                        if not line:
                            continue
                        try:
                            otp_dict = json.loads(line)
                            if username in otp_dict:
                                return otp_dict[username]
                        except json.JSONDecodeError:
                            print(f"JSON解析失败，跳过行: {line}")
                            continue
        except Exception as e:
            print(f"读取OTP文件出错: {e}")
        time.sleep(0.5)  # 检查间隔
    return None

if __name__=="__main__":
    # Step1: user login action triggers that firewall send otp_code to smtp server
    ipstr = sys.argv[1]
    username = sys.argv[2]
    login_user(ipstr,username)
    time.sleep(5)

    # Step2: get otp_code
    otp = get_otp(username)
    # print(otp)
    if otp:
        print(f"Get {username} Otp Code: {otp}")
        login_2FA(otp)
    else:
        print(f"获取 {username} 的OTP超时")
    time.sleep(10)

