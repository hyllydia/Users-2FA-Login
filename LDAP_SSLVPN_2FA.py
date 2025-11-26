# -*- coding: utf-8 -*-
# @Time    : 6/27/25
# @Author  : Yuling Hou
# @File    : LDAP_SSLVPN_2FA.py
# @Software: PyCharm
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import requests
import threading
import time
import json
import logging
from datetime import datetime
from requests.auth import HTTPBasicAuth
import os
import config.firewall_info

"""
ReadMe ladpusers test1~test6000 sslvpn portal 2FA login.
Step1.登录防火墙 login,触发发送验证码给SMTP server;
Step2.从SMTP body中获取验证码， 将用户名和验证码做成字典 {"ltest1":"haifhe284994"},用户名和密码怎么一一对应呢？
smtp server body中会获取邮箱比如ltest1@163.com, 那么将ltest正则匹配出来，和验证码组成字典；
Step3.将收到的验证码通过API做2FA登录
"""

FIREWALL_IP = "10.7.5.155:4433"
API_AUTH = f"https://{FIREWALL_IP}/api/sonicos/auth"
API_OTP = f"https://{FIREWALL_IP}/api/sonicos/one-time-password"
FIREWALL_TYPE = "5700"

# 会话保持
session = requests.Session()
session.verify = False

#OTP_FILE = "./data/5700_GreatWall_otpcode.json"  # 与服务器相同的文件路径

OTP_FILE = "./data/"+ FIREWALL_TYPE +"_GreatWall_otpcode.json"

def login_user(username,password):
    body = {"domain":"LocalDomain","override": False,"snwl": True}
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-SNWL-API-Scope': 'extended',  # 关键头
        'X-SNWL-Timer': 'no-reset'  # 关键头
    }
    try:
        response = session.post(API_AUTH, auth=HTTPBasicAuth(username=username, password=password), data=json.dumps(body),
                          headers=headers)
        if response.status_code == 200:
            print(f"{username} login sucess!")
            resp_data = response.json()


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
if __name__ == "__main__":
    while True:
        for i in range(1,6001):
            print(f"******========test{i}=======******")
            #Step1: user login action triggers that firewall send otp_code to smtp server
            username = "test" +str(i)
            password ="hyllydia@2020"
            print(f"{username} login:")
            login_user(username=username, password=password)
            time.sleep(5)

            #Step2: get otp_code
            otp = get_otp(username)
            #print(otp)
            if otp:
                print(f"Get {username} Otp Code: {otp}")
                login_2FA(otp)
            else:
                print(f"获取 {username} 的OTP超时")
            time.sleep(10)


