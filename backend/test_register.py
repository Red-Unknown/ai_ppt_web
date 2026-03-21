#!/usr/bin/env python3
"""
测试注册功能的脚本
"""

from app.services.Register import register_service
from app.services.Login import login_service
import time

print("=== 测试注册功能 ===")

# 测试1: 发送验证码
print("\n1. 测试发送验证码:")
phone = "13800138000"
success, message = register_service.send_verification_code(phone)
print(f"发送验证码结果: {success}, {message}")

# 测试2: 验证验证码（使用错误的验证码）
print("\n2. 测试验证错误验证码:")
success, message = register_service.verify_verification_code(phone, "123456")
print(f"验证错误验证码结果: {success}, {message}")

# 测试3: 注册学生
print("\n3. 测试注册学生:")
# 注意：这里需要使用真实的验证码，需要从控制台输出中获取
# 由于我们是模拟发送，验证码会打印在控制台
# 这里我们使用一个假的验证码，实际测试时需要替换
code = "406617"  # 使用上面生成的验证码
success, result = register_service.register_student(
    username="teststudent",
    password="Test123456!",
    name="测试学生",
    student_id="20240001",
    phone=phone
)
print(f"注册学生结果: {success}, {result}")

# 测试4: 登录
print("\n4. 测试登录:")
success, result = login_service.authenticate("teststudent", "Test123456!")
print(f"登录结果: {success}, {result}")

# 测试5: 验证会话
if success:
    session_id = result.get("session_id")
    print("\n5. 测试验证会话:")
    success, result = login_service.validate_session(session_id)
    print(f"验证会话结果: {success}, {result}")

print("\n=== 测试完成 ===")
