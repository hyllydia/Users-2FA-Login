# -*- coding: utf-8 -*-
# @Time    : 10/22/25
# @Author  : Yuling Hou
# @File    : nx_data.py
# @Software: PyCharm

import os

# BASIC CONFIGURATION
FIREWALL_TYPE = "680"
TESTBED_NAME = "GreatWall"
USERNAME_PREFIX = "emuser"
PASSWORD = "hyllydia@2020"
SERVER = "10.7.5.146:4433"
DOMAIN = "LocalDomain"
MAX_USERS = 150

#LOGOUT USERS
WEBGUI_IP = "10.7.5.146"
ADMIN = "admin"
PASSWD = "123qwe!@#QWE"
#Client_Virtual_Start_IP = "172.148.100.1"

# 当前文件所在目录
THIS_DIR = os.path.dirname(os.path.abspath(__file__))

# expect 脚本绝对路径
SCRIPT_PATH = os.path.join(THIS_DIR, "Script3_NetExtender2FA_connect.exp")
#SCRIPT_PATH = os.path.join(THIS_DIR, "test.exp")

OTP_FILE = os.path.join(THIS_DIR,f"../data/{FIREWALL_TYPE}_{TESTBED_NAME}_otpcode.json")

MAPPING_FILE = os.path.join(THIS_DIR,f"./user_ip_mapping.txt")

LOG_DIR = os.path.join(THIS_DIR, "logs")
