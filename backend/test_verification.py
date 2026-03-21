#!/usr/bin/env python3
"""
测试验证码功能的脚本
"""

from app.services.Register import register_service
import time

print("=== 测试验证码功能 ===")

# 测试1: 发送验证码（正确的手机号）
print("\n1. 测试发送验证码（正确的手机号）:")
phone = "13800138000"
success, message = register_service.send_verification_code(phone)
print(f"发送验证码结果: {success}, {message}")

# 测试2: 发送验证码（错误的手机号格式）
print("\n2. 测试发送验证码（错误的手机号格式）:")
wrong_phone = "123456789"
success, message = register_service.send_verification_code(wrong_phone)
print(f"发送验证码结果: {success}, {message}")

# 测试3: 发送验证码（频率限制）
print("\n3. 测试发送验证码（频率限制）:")
success, message = register_service.send_verification_code(phone)
print(f"发送验证码结果: {success}, {message}")

# 测试4: 验证验证码（正确的验证码）
print("\n4. 测试验证验证码（正确的验证码）:")
# 注意：这里需要使用真实的验证码，需要从控制台输出中获取
# 由于我们是模拟发送，验证码会打印在控制台
# 这里我们使用一个假的验证码，实际测试时需要替换
code = "203024"  # 使用上面生成的验证码
success, message = register_service.verify_verification_code(phone, code)
print(f"验证验证码结果: {success}, {message}")

# 测试5: 验证验证码（错误的验证码）
print("\n5. 测试验证验证码（错误的验证码）:")
wrong_code = "654321"
success, message = register_service.verify_verification_code(phone, wrong_code)
print(f"验证验证码结果: {success}, {message}")

# 测试6: 验证验证码（验证码不存在）
print("\n6. 测试验证验证码（验证码不存在）:")
success, message = register_service.verify_verification_code("13800138001", "123456")
print(f"验证验证码结果: {success}, {message}")

print("\n=== 测试完成 ===")
