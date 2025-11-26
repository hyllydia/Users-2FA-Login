# -*- coding: utf-8 -*-
# @Time    : 10/21/25
# @Author  : Yuling Hou
# @File    : NetExtender2FA_manage.py
# @Software: PyCharm
import subprocess
import time
import os
import sys
from nx_data import USERNAME_PREFIX, PASSWORD, SERVER, DOMAIN, MAX_USERS, SCRIPT_PATH, OTP_FILE,MAPPING_FILE


def wait_for_ppp_ip(username, timeout=60):
    """等待PPP IP地址出现"""
    print(f"[{username}] Waiting for PPP connection...")
    start_time = time.time()

    while time.time() - start_time < timeout:
        ip = get_ppp_ip_address()
        if ip:
            return ip
        time.sleep(3)  # 每3秒检查一次

    return None


def get_ppp_ip_address():
    """获取最新的PPP IP地址"""
    try:
        # 使用ip命令查找PPP接口
        result = subprocess.run(["ip", "-o", "addr", "show"], capture_output=True, text=True)
        lines = result.stdout.split('\n')

        ppp_ips = []
        for line in lines:
            if 'ppp' in line and 'inet ' in line:
                parts = line.split()
                if len(parts) >= 4:
                    interface = parts[1]
                    ip = parts[3].split('/')[0]
                    ppp_ips.append((interface, ip))

        # 返回最新的PPP IP（如果有多个）
        if ppp_ips:
            interface, ip = ppp_ips[-1]  # 取最后一个，通常是最新的
            return ip

        return None

    except Exception as e:
        print(f"   Error getting PPP IP: {e}")
        return None


def connect_vpn_with_tmux():
    """使用tmux为每个用户创建独立终端会话"""
    print(f"[*] Starting VPN connections for {MAX_USERS} users using TMUX")

    # 映射文件路径
    #mapping_file = "user_ip_mapping.txt"

    # 清空或创建映射文件
    with open(MAPPING_FILE, "w") as f:
        f.write("# User to IP Mapping\n")
        f.write("# Format: username,ip_address\n\n")

    successful_users = 0
    mapped_users = 0

    # 检查tmux是否可用
    try:
        subprocess.run(["tmux", "-V"], check=True, capture_output=True)
    except:
        print(" Error: tmux is not installed or not in PATH")
        sys.exit(1)

    for i in range(1, MAX_USERS + 1):
        username = f"{USERNAME_PREFIX}{i}"
        print(f"\n{'=' * 60}")
        print(f"[*] STARTING USER {i}/{MAX_USERS}: {username}")
        print(f"{'=' * 60}")

        try:
            # 为每个用户创建独立的tmux会话
            session_name = f"sslvpn_{username}"

            # 创建tmux会话并在其中运行expect脚本
            cmd = [
                "tmux", "new-session", "-d", "-s", session_name,
                SCRIPT_PATH, username, PASSWORD, DOMAIN, SERVER, OTP_FILE, "120"
            ]

            print(f"[{username}] Creating tmux session: {session_name}")
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                #print(f" [{username}] TMUX session created successfully!!!")
                successful_users += 1
            else:
                print(f"[{username}] Failed to create TMUX session: {result.stderr}")
                continue

            # 等待更长时间让用户完成登录和PPP连接建立
            wait_time = 25  # 增加等待时间，确保NetExtender完全连接
            print(f"[{username}] Waiting {wait_time} seconds for full connection...")
            time.sleep(wait_time)

            # 检查会话是否还在运行
            check_cmd = ["tmux", "has-session", "-t", session_name]
            check_result = subprocess.run(check_cmd, capture_output=True)
            if check_result.returncode == 0:
                print(f"[{username}] Session is running normally")

                # 等待并获取PPP IP地址
                ppp_ip = wait_for_ppp_ip(username, timeout=30)
                if ppp_ip:
                    # 写入映射文件
                    with open(MAPPING_FILE, "a") as f:
                        f.write(f"{username},{ppp_ip}\n")
                    print(f"[{username}] Mapping saved: {username} -> {ppp_ip}")
                    mapped_users += 1
                else:
                    print(f"[{username}] No PPP IP found after waiting, user may still be connecting")
            else:
                print(f"[{username}] Session failed or ended unexpectedly")

            # 等待一段时间再开始下一个用户
            if i < MAX_USERS:
                wait_time = 5  # 减少等待时间
                print(f"\n[*] Waiting {wait_time} seconds before starting next user...")
                time.sleep(wait_time)

        except Exception as e:
            print(f"[{username}] Exception: {e}")
            continue

    # print(f"\n[*] All {MAX_USERS} users processed")
    # print(f"[*] Successful sessions: {successful_users}/{MAX_USERS}")
    # print(f"[*] Users with PPP IP: {mapped_users}/{MAX_USERS}")
    # print(f"[*] Mapping file created: {mapping_file}")

    # 显示映射文件内容
    # print(f"\n[*] User to IP Mapping:")
    # try:
    #     with open(MAPPING_FILE, "r") as f:
    #         for line in f:
    #             print(f"    {line.strip()}")
    # except Exception as e:
    #     print(f"Error reading mapping file: {e}")


def list_tmux_sessions():
    """列出所有VPN相关的tmux会话"""
    print(f"\n[*] Current SSLVPN TMUX Sessions:")
    try:
        result = subprocess.run(["tmux", "ls"], capture_output=True, text=True)
        if result.returncode == 0:
            sessions = [line for line in result.stdout.split('\n') if line and 'sslvpn_' in line]
            if sessions:
                for session in sessions:
                    print(f"    {session}")
            else:
                print("    No active VPN sessions")
        else:
            print("    Failed to list sessions")
    except Exception as e:
        print(f"    Error: {e}")


if __name__ == "__main__":
    if not os.path.exists(SCRIPT_PATH):
        print(f"Error: Expect script not found at {SCRIPT_PATH}")
        sys.exit(1)

    # 检查是否已存在会话
    #list_tmux_sessions()

    # 开始创建会话
    connect_vpn_with_tmux()

    # 显示最终状态
    #list_tmux_sessions()