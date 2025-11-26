# -*- coding: utf-8 -*-
# @Time    : 9/29/25
# @Author  : Yuling Hou
# @File    : config_data.py
# @Software: PyCharm

#BASIC CONFIGURATION
FIREWALL_IP = "172.185.0.68:4433"
FIREWALL_TYPE = "680"
Testbed_Name = "GreatWall"
ADMIN ="admin"
WEBGUI_IP = "10.7.5.146"
PASSWD = "123qwe!@#QWE"
PASSWORD = "sonicwall2010"
SSLVPNDOMAIN = "LocalDomain"
BASE_IFACE = "ens192"
USER_COUNT = 250
START_IP_A = 1
USER_PREFIX = "sslvpnLouser"

MAPPING_FILE = f"user_iface_{USER_COUNT}.txt"
# file name is from SMTP_Server.py parameter from_user , every type has its different name
# get the file name from the log dic
OTP_FILE = f"../data/{FIREWALL_TYPE}_{Testbed_Name}_otpcode.json"

API_AUTH = f"https://{FIREWALL_IP}/api/sonicos/auth"
API_OTP = f"https://{FIREWALL_IP}/api/sonicos/one-time-password"
API_DELETE = f"https://{FIREWALL_IP}/api/"


