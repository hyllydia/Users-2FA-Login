# -*- coding: utf-8 -*-
# @Time    : 9/29/25
# @Author  : Yuling Hou
# @File    : Script1_delete_otp_files.py
# @Software: PyCharm
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from config_data import OTP_FILE, MAPPING_FILE

def remove_otp_file():
    if os.path.exists(OTP_FILE):
        try:
            os.remove(OTP_FILE)
            print(f"Old OTP file deleted: {OTP_FILE}")
        except Exception as e:
            print(f"Failed to delete OTP file: {e}")
    else:
        print("No OTP file found, no cleanup needed")

def remove_mapping_file():
    if os.path.exists(MAPPING_FILE):
        try:
            os.remove(MAPPING_FILE)
            print(f"Old mapping file deleted: {MAPPING_FILE}")
        except Exception as e:
            print(f"Failed to delete mapping file: {e}")
    else:
        print("No mapping file found, no cleanup needed")

if __name__ == "__main__":
    remove_otp_file()
    remove_mapping_file()
