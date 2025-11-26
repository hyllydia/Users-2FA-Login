# -*- coding: utf-8 -*-
# @Time    : 11/7/25
# @Author  : Yuling Hou
# @File    : API_Server_OTPCode.py
# @Software: PyCharm
# !/usr/bin/env python3
from flask import Flask, request, jsonify
import json
import os
import time

app = Flask(__name__)


@app.route('/api/otp', methods=['POST'])
def save_otp():
    """接收并保存OTP文件到本地data目录"""
    data = request.json
    from_user = data.get('from_user')
    to_user = data.get('to_user')
    otp_code = data.get('otp_code')

    if from_user and to_user and otp_code:
        try:
            # 确保data目录存在
            data_dir = os.path.join(os.path.dirname(__file__), 'data')
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
                print(f"Created data directory: {data_dir}")

            # 文件名格式：480_GreatWall_otpcode.json
            filename = f"{from_user}_otpcode.json"
            filepath = os.path.join(data_dir, filename)

            # 读取或创建文件
            existing_data = {}
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                except:
                    existing_data = {}

            # 更新数据
            existing_data[to_user] = otp_code

            # 保存文件
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)

            print(f"OTP saved: {filepath}")
            print(f"Content: {existing_data}")

            return jsonify({'status': 'success'})

        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Missing data'}), 400


if __name__ == '__main__':
    print("OTP API Server running on http://0.0.0.0:5000")
    print("OTP files will be saved in ./data/")
    app.run(host='0.0.0.0', port=5000, debug=True)