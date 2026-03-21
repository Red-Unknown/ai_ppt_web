#!/usr/bin/env python3
"""
测试完整注册流程的脚本
"""

import requests
import json

BASE_URL = "http://localhost:8000"

print("=== 测试完整注册流程 ===")

# 测试1: 发送验证码
print("\n1. 测试发送验证码:")
phone = "13800138001"
send_code_url = f"{BASE_URL}/api/v1/register/send-code"
send_code_data = {"phone": phone}
response = requests.post(send_code_url, json=send_code_data)
print(f"发送验证码响应: {response.status_code}, {response.json()}")

# 测试2: 验证验证码
print("\n2. 测试验证验证码:")
# 注意：这里需要使用真实的验证码，需要从后端控制台输出中获取
# 由于我们是模拟发送，验证码会打印在后端控制台
code = "123456"  # 实际测试时需要替换为后端控制台输出的验证码
verify_code_url = f"{BASE_URL}/api/v1/register/verify-code"
verify_code_data = {"phone": phone, "code": code}
response = requests.post(verify_code_url, json=verify_code_data)
print(f"验证验证码响应: {response.status_code}, {response.json()}")

# 测试3: 注册学生
print("\n3. 测试注册学生:")
register_url = f"{BASE_URL}/api/v1/register/student"
register_data = {
    "username": "teststudent2",
    "password": "Test123456!",
    "name": "测试学生2",
    "student_id": "20240002",
    "phone": phone,
    "code": code
}
response = requests.post(register_url, json=register_data)
print(f"注册学生响应: {response.status_code}, {response.json()}")

# 测试4: 登录
print("\n4. 测试登录:")
login_url = f"{BASE_URL}/api/v1/login/"
login_data = {
    "identifier": "teststudent2",
    "password": "Test123456!"
}
response = requests.post(login_url, json=login_data)
print(f"登录响应: {response.status_code}, {response.json()}")

print("\n=== 测试完成 ===")
