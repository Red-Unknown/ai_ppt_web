from typing import Dict, Optional, Tuple
import hashlib
import re
import random
import time

class RegisterService:
    def __init__(self):
        # 内存数据结构模拟数据库
        # 这里使用与LoginService相同的存储结构，以便共享用户数据
        from app.services.Login import login_service
        self.users = login_service.users
        self.login_service = login_service
        # 存储验证码
        self.verification_codes = {}
        self.code_expiry = 300  # 5分钟过期
    
    def _hash_password(self, password: str) -> str:
        """密码哈希处理"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _generate_verification_code(self) -> str:
        """生成6位数字验证码"""
        return ''.join(random.choices('0123456789', k=6))
    
    def send_verification_code(self, phone: str) -> Tuple[bool, Optional[str]]:
        """发送验证码
        注意：这里是模拟实现，实际项目中需要集成阿里云或腾讯云短信服务
        """
        # 验证手机号格式
        if not re.match(r'^1[3-9]\d{9}$', phone):
            return False, "手机号格式不正确"
        
        # 生成验证码
        code = self._generate_verification_code()
        
        # 存储验证码和过期时间
        self.verification_codes[phone] = {
            "code": code,
            "expires_at": time.time() + self.code_expiry
        }
        
        # 模拟发送短信
        print(f"向手机号 {phone} 发送验证码: {code}")
        
        return True, "验证码发送成功"
    
    def verify_verification_code(self, phone: str, code: str) -> Tuple[bool, Optional[str]]:
        """验证验证码"""
        # 检查验证码是否存在
        if phone not in self.verification_codes:
            return False, "验证码不存在"
        
        # 检查验证码是否过期
        code_info = self.verification_codes[phone]
        if time.time() > code_info["expires_at"]:
            del self.verification_codes[phone]
            return False, "验证码已过期"
        
        # 检查验证码是否正确
        if code_info["code"] != code:
            return False, "验证码不正确"
        
        # 验证码验证成功后删除
        del self.verification_codes[phone]
        
        return True, "验证码验证成功"
    
    def check_password_strength(self, password: str) -> Dict:
        """检查密码强度"""
        strength = 0
        suggestions = []
        
        # 长度检查
        if len(password) >= 8:
            strength += 1
        else:
            suggestions.append("密码长度应至少为8位")
        
        if len(password) >= 12:
            strength += 1
        
        # 包含数字
        if any(char.isdigit() for char in password):
            strength += 1
        else:
            suggestions.append("密码应包含数字")
        
        # 包含小写字母
        if any(char.islower() for char in password):
            strength += 1
        else:
            suggestions.append("密码应包含小写字母")
        
        # 包含大写字母
        if any(char.isupper() for char in password):
            strength += 1
        else:
            suggestions.append("密码应包含大写字母")
        
        # 包含特殊字符
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            strength += 1
        else:
            suggestions.append("密码应包含特殊字符")
        
        # 评估强度等级
        if strength <= 2:
            level = "弱"
        elif strength <= 4:
            level = "中"
        else:
            level = "强"
        
        return {
            "strength": strength,
            "level": level,
            "suggestions": suggestions
        }
    
    def _validate_student_register(self, username: str, password: str, name: str, student_id: str) -> Tuple[bool, Optional[str]]:
        """验证学生注册信息"""
        # 验证用户名格式（学生用户名通常为学号）
        if not re.match(r'^[a-zA-Z0-9]{6,20}$', username):
            return False, "用户名格式不正确，应包含6-20位字母和数字"
        
        # 验证密码强度
        if len(password) < 8 or len(password) > 16:
            return False, "密码长度应在8-16位之间"
        
        if not any(char.isdigit() for char in password) or not any(char.isalpha() for char in password):
            return False, "密码至少包含数字和字母两种元素"
        
        # 验证姓名
        if not name or len(name) > 20:
            return False, "姓名不能为空且长度不能超过20位"
        
        # 验证学号
        if not re.match(r'^[a-zA-Z0-9]{6,20}$', student_id):
            return False, "学号格式不正确，应包含6-20位字母和数字"
        
        # 检查用户名是否已存在
        if username in self.users:
            return False, "用户名已存在"
        
        return True, None
    
    def _validate_teacher_register(self, username: str, password: str, name: str, teacher_id: str) -> Tuple[bool, Optional[str]]:
        """验证教师注册信息"""
        # 验证用户名格式（教师用户名通常为工号）
        if not re.match(r'^[a-zA-Z0-9]{6,20}$', username):
            return False, "用户名格式不正确，应包含6-20位字母和数字"
        
        # 验证密码强度
        if len(password) < 8 or len(password) > 16:
            return False, "密码长度应在8-16位之间"
        
        if not any(char.isdigit() for char in password) or not any(char.isalpha() for char in password):
            return False, "密码至少包含数字和字母两种元素"
        
        # 验证姓名
        if not name or len(name) > 20:
            return False, "姓名不能为空且长度不能超过20位"
        
        # 验证教师ID
        if not re.match(r'^[a-zA-Z0-9]{6,20}$', teacher_id):
            return False, "教师ID格式不正确，应包含6-20位字母和数字"
        
        # 检查用户名是否已存在
        if username in self.users:
            return False, "用户名已存在"
        
        return True, None
    
    def register_student(self, username: str, password: str, name: str, student_id: str) -> Tuple[bool, Optional[Dict]]:
        """学生注册"""
        # 验证注册信息
        valid, error = self._validate_student_register(username, password, name, student_id)
        if not valid:
            return False, {"error": error}
        
        # 注册用户
        self.users[username] = {
            "password": self._hash_password(password),
            "role": "student",
            "name": name,
            "student_id": student_id
        }
        
        # 注册成功后自动登录
        login_success, login_result = self.login_service.authenticate(username, password)
        if login_success:
            return True, {
                "username": username,
                "role": "student",
                "name": name,
                "student_id": student_id,
                "session_id": login_result.get("session_id"),
                "user": login_result.get("user")
            }
        else:
            return True, {
                "username": username,
                "role": "student",
                "name": name,
                "student_id": student_id
            }
    
    def register_teacher(self, username: str, password: str, name: str, teacher_id: str) -> Tuple[bool, Optional[Dict]]:
        """教师注册"""
        # 验证注册信息
        valid, error = self._validate_teacher_register(username, password, name, teacher_id)
        if not valid:
            return False, {"error": error}
        
        # 注册用户
        self.users[username] = {
            "password": self._hash_password(password),
            "role": "teacher",
            "name": name,
            "teacher_id": teacher_id
        }
        
        # 注册成功后自动登录
        login_success, login_result = self.login_service.authenticate(username, password)
        if login_success:
            return True, {
                "username": username,
                "role": "teacher",
                "name": name,
                "teacher_id": teacher_id,
                "session_id": login_result.get("session_id"),
                "user": login_result.get("user")
            }
        else:
            return True, {
                "username": username,
                "role": "teacher",
                "name": name,
                "teacher_id": teacher_id
            }

# 单例模式
register_service = RegisterService()