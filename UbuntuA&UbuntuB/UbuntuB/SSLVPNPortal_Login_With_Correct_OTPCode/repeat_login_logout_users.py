# -*- coding: utf-8 -*-
# @Time    : 9/29/25
# @Author  : Yuling Hou
# @File    : repeat_login_logout_users.py
# @Software: PyCharm
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
from config_data import BASE_IFACE

while True:
    print(f"{'=' * 8} Step1: Delete OTP&MAPPING Files{'=' * 8}")
    os.system("python3 Script1_delete_otp_files.py")
    time.sleep(10)
    print(f"{'=' * 8} Step2: Down Virtual Interfaces{'=' * 8}")
    os.system("python3 Script2_down_virtual_ifaces.py")
    time.sleep(10)
    print(f"{'=' * 8} Step3: Add Virtual Interfaces for {BASE_IFACE}{'=' * 8}")
    os.system("python3 Script3_add_virtual_ifaces.py")
    time.sleep(10)
    #print(f"{'=' * 8} Step4: Do SSLVPN Portal 2FA Login{'=' * 8}")
    print(f"{'=' * 8} Step6: Do SSLVPN Portal 2FA Login API{'=' * 8}")
    #os.system("python3 Script4_login_2FA.py")
    os.system("python3 Script6_API_login_2FA.py")
    time.sleep(300)
    print(f"{'=' * 8} Step5: Logout SSLVPN Portal Users{'=' * 8}")
    os.system("python3 Script5_logout_sslvpnportal_users.py")
    time.sleep(300)

    time.sleep(120)
