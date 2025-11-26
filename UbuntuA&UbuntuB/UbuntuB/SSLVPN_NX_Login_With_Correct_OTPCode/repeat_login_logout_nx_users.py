# -*- coding: utf-8 -*-
# @Time    : 10/28/25
# @Author  : Yuling Hou
# @File    : repeat_login_logout_users.py
# @Software: PyCharm
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time

while True:
    print(f"{'=' *8} Step1: Delete OTP&MAPPING Files{'=' *8}")
    os.system("python3 Script1_delete_otp_files.py")
    time.sleep(10)
    print(f"{'=' * 8} Step2: Do SSLVPN NetExtender 2FA Login{'=' * 8}")
    os.system("python3 Script2_NetExtender2FA_manage.py")
    time.sleep(180)
    print(f"{'=' * 8} Step3: Logout SSLVPN NetExtender Users{'=' * 8}")
    os.system("python3 Script4_logout_sslvpn_nx_users.py")
    time.sleep(30)

    time.sleep(120)
