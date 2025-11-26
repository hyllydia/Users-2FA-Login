# -*- coding: utf-8 -*-
# @Time    : 7/9/25
# @Author  : Yuling Hou
# @File    : NetExtender2FA_manage.py
# @Software: PyCharm
import multiprocessing
import subprocess
import time
import os
import sys
from nx_data import USERNAME_PREFIX, PASSWORD, SERVER, DOMAIN, MAX_USERS, SCRIPT_PATH, OTP_FILE


def connect_vpn(username):
    """独立的VPN连接函数，用于多进程"""
    print(f"Starting VPN connection for {username}")
    try:
        if not os.access(SCRIPT_PATH, os.X_OK):
            os.chmod(SCRIPT_PATH, 0o755)
        # 使用Popen但不等待完成
        process = subprocess.Popen(
            [SCRIPT_PATH, username, PASSWORD, DOMAIN, SERVER,OTP_FILE],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        # 实时输出处理
        def handle_output(stream, is_stderr=False):
            for line in stream:
                if is_stderr:
                    print(f"[{username} ERROR] {line}", end='', file=sys.stderr)
                else:
                    print(f"[{username}] {line}", end='')

        # 为输出创建线程
        import threading
        threading.Thread(target=handle_output, args=(process.stdout,)).start()
        threading.Thread(target=handle_output, args=(process.stderr, True)).start()

        return process

    except Exception as e:
        print(f"Error for {username}: {str(e)}")
        return None


if __name__ == "__main__":
    if not os.path.exists(SCRIPT_PATH):
        print(f"Error: Shell script not found at {SCRIPT_PATH}")
        sys.exit(1)

    # 创建进程池
    processes = []

    for i in range(1, MAX_USERS + 1):
        username = f"{USERNAME_PREFIX}{i}"
        p = multiprocessing.Process(
            target=connect_vpn,
            args=(username,)
        )
        p.start()
        processes.append(p)
        time.sleep(5)  # 避免同时发起太多连接

    # 等待所有进程
    for p in processes:
        p.join()