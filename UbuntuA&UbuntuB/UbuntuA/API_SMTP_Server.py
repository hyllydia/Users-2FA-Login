# -*- coding: utf-8 -*-
# @Time    : 11/6/25
# @Author  : Yuling Hou
# @File    : API_SMTP_Server.py
# @Software: PyCharm
import os
import argparse
import ssl
import re
import shutil
from email import policy
from email.parser import BytesParser
import time
import json
from datetime import datetime
import requests

try:
    from aiosmtpd.controller import Controller
except ImportError as e:
    try:
        os.system('sudo pip3 install aiosmtpd --proxy="http://10.50.128.110:3128"')
        from aiosmtpd.controller import Controller

        print('aiosmtpd have been installed successfully! ! !')
    except Exception as e:
        print("======aiosmtpd installation failed======\n{}\n".format(e))

# create params used to run script by cmd
arums = argparse.ArgumentParser(description="The arguments used to smtp and smtps server")
arums.add_argument('--ip', help="The bound IP address")
arums.add_argument('--port', default=1025, help="The smtp service binding port")
arums.add_argument('--ssl_port', default=1465, help="The smtp-ssl service binding port")
arums.add_argument('--api_url', default="http://localhost:5000", help="API server URL")
arums = arums.parse_args()

# 全局变量 - UbuntuB的API地址
UBUNTU_B_API_URL = "http://10.7.13.136:5000/api/otp"


class CustomHandler:
    def __init__(self, api_url):
        self.api_url = api_url

    async def handle_DATA(self, server, session, envelope):
        peer = session.peer
        mail_from = envelope.mail_from
        rcpt_tos = envelope.rcpt_tos
        data = envelope.content  # type: bytes

        # 获取当前时间戳
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 从发件人提取用户名 (如 480_GreatWall)
        from_user = re.findall(r'^([^@]+)@', mail_from)[0] if '@' in mail_from else mail_from

        # 从收件人提取用户名 (如 emuser1)
        to_user = re.findall(r'^([^@]+)@', rcpt_tos[0])[0] if rcpt_tos and '@' in rcpt_tos[0] else rcpt_tos[0]

        # 解析邮件内容
        msg = BytesParser(policy=policy.default).parsebytes(data)
        body = msg.get_payload(decode=True)
        otp_code = body.decode(msg.get_content_charset() or 'utf-8').strip()

        # 1. 写入日志文件
        log_filename = f"log/{from_user}.log"
        with open(log_filename, 'a', encoding='utf-8') as log_file:
            log_file.write(f"\n{'=' * 50}\n")
            log_file.write(f"Time: {current_time}\n")
            log_file.write(f"From: {mail_from}\n")
            log_file.write(f"To: {', '.join(rcpt_tos)}\n")
            log_file.write(f"Peer: {peer}\n")
            log_file.write(f"Data size: {len(data)} bytes\n")
            log_file.write(f"OTP Code: {otp_code}\n")
            log_file.write(f"{'=' * 50}\n")

        # 2. 写入OTP数据文件
        data_filename = f"data/{from_user}_otpcode.json"
        try:
            existing_data = {}
            if os.path.exists(data_filename):
                try:
                    with open(data_filename, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                except (json.JSONDecodeError, Exception):
                    existing_data = {}

            existing_data[to_user] = otp_code

            with open(data_filename, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())

        except Exception as e:
            print(f"[SMTP] Error saving OTP data: {e}")
            return '550 Error saving OTP data'

        # 3. 发送OTP到API服务器
        self.send_otp_to_api(from_user, to_user, otp_code)

        # 控制台输出
        print(f"\n{'=' * 50}")
        print(f"Time: {current_time}")
        print(f"From: {mail_from}")
        print(f"To: {', '.join(rcpt_tos)}")
        print(f"Peer: {peer}")
        print(f"Data size: {len(data)} bytes")
        print(f"OTP Code: {otp_code}")
        print(f"Log saved to: {log_filename}")
        print(f"Data saved to: {data_filename}")
        print(f"{'=' * 50}")

        return '250 OK'

    def send_otp_to_api(self, from_user, to_user, otp_code):
        """发送OTP到UbuntuB的API服务器"""
        try:
            data = {
                'from_user': from_user,
                'to_user': to_user,
                'otp_code': otp_code
            }

            # 使用全局变量发送到UbuntuB的API
            response = requests.post(
                UBUNTU_B_API_URL,
                json=data,
                timeout=5
            )

            if response.status_code == 200:
                print(f"OTP sent to UbuntuB successfully")
            else:
                print(f"Failed to send OTP: {response.text}")

        except Exception as e:
            print(f"API error: {e}")


if __name__ == '__main__':
    # 初始化时清空数据文件夹
    if os.path.exists('data'):
        shutil.rmtree('data')
    os.makedirs('data', exist_ok=True)
    os.makedirs('log', exist_ok=True)

    print("=" * 60)
    print("SMTP Server Started")
    print(f"Data directory: {os.path.abspath('data')}")
    print(f"Log directory: {os.path.abspath('log')}")
    print(f"API Server: {UBUNTU_B_API_URL}")
    print("=" * 60)

    try:
        handler = CustomHandler(api_url=arums.api_url)
        # init smtp controller
        smtp_controller = Controller(handler, hostname=arums.ip, port=arums.port, ready_timeout=10.0)
        # Load SSL context
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain('./smtp_ssl_cert/SMTPS_Cert.pem', './smtp_ssl_cert/SMTPS_Private_Key.pem')
        # init smtp ssl controller
        smtps_controller = Controller(handler, hostname=arums.ip, port=arums.ssl_port, ssl_context=context,
                                      ready_timeout=10.0)
        # Run the event loop in a separate thread.
        smtp_controller.start()
        smtps_controller.start()

        print("Press Ctrl+C to stop server and exit.\n")

        # 保持服务器运行
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nShutting down servers...")
    except Exception as e:
        print(f'Error: {e}')
    finally:
        smtp_controller.stop()
        smtps_controller.stop()
        print("Servers stopped.")