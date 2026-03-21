from typing import Dict, Optional, Tuple
import re
import random
import time
import os
import bcrypt
from sqlalchemy.orm import Session
from app.core.database import get_db, User
from app.services.Login import login_service

class RegisterService:
    def __init__(self):
        # 存储验证码（暂时使用内存存储）
        self.verification_codes = {}
        self.code_expiry = 300  # 5分钟过期
    
    def _hash_password(self, password: str) -> str:
        """密码哈希处理"""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    def _generate_verification_code(self) -> str:
        """生成6位数字验证码"""
        return ''.join(random.choices('0123456789', k=6))
    
    def send_verification_code(self, phone: str) -> Tuple[bool, Optional[str]]:
        """发送验证码
        注意：短信服务暂未开通，功能已暂停
        """
        # 短信服务暂未开通，功能已暂停
        return False, "短信服务暂未开通，验证码功能暂不可用"
    
    def verify_verification_code(self, phone: str, code: str) -> Tuple[bool, Optional[str]]:
        """验证验证码"""
        # 验证手机号格式
        if not re.match(r'^1[3-9]\d{9}$', phone):
            return False, "手机号格式不正确"
        
        # 检查验证码是否存在
        if phone not in self.verification_codes:
            return False, "验证码不存在，请先获取验证码"
        
        try:
            # 检查验证码是否过期
            code_info = self.verification_codes[phone]
            if time.time() > code_info["expires_at"]:
                del self.verification_codes[phone]
                return False, "验证码已过期，请重新获取"
            
            # 检查验证码是否正确
            if code_info["code"] != code:
                return False, "验证码不正确，请重新输入"
            
            # 验证码验证成功后删除
            del self.verification_codes[phone]
            
            return True, "验证码验证成功"
        except Exception as e:
            # 处理可能的异常情况
            print(f"验证验证码失败: {str(e)}")
            return False, f"验证验证码失败: {str(e)}"
    
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
    
    def _validate_student_register(self, username: str, password: str, name: str, student_id: str, phone: str) -> Tuple[bool, Optional[str]]:
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
        
        # 验证手机号
        if not re.match(r'^1[3-9]\d{9}$', phone):
            return False, "手机号格式不正确，请输入中国大陆11位手机号"
        
        # 检查用户名、学号、手机号是否已存在
        db = next(get_db())
        try:
            if db.query(User).filter(User.user_name == username).first():
                return False, "用户名已存在"
            if db.query(User).filter(User.student_id == student_id).first():
                return False, "学号已被注册"
            if db.query(User).filter(User.phone == phone).first():
                return False, "手机号已被注册"
            return True, None
        except Exception as e:
            print(f"验证学生注册信息失败: {str(e)}")
            return False, "验证失败，请稍后重试"
        finally:
            db.close()
    
    def _validate_teacher_register(self, username: str, password: str, name: str, teacher_id: str, phone: str) -> Tuple[bool, Optional[str]]:
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
        
        # 验证手机号
        if not re.match(r'^1[3-9]\d{9}$', phone):
            return False, "手机号格式不正确，请输入中国大陆11位手机号"
        
        # 检查用户名、教师ID、手机号是否已存在
        db = next(get_db())
        try:
            if db.query(User).filter(User.user_name == username).first():
                return False, "用户名已存在"
            if db.query(User).filter(User.teacher_id == teacher_id).first():
                return False, "教师ID已被注册"
            if db.query(User).filter(User.phone == phone).first():
                return False, "手机号已被注册"
            return True, None
        except Exception as e:
            print(f"验证教师注册信息失败: {str(e)}")
            return False, "验证失败，请稍后重试"
        finally:
            db.close()
    
    def register_student(self, username: str, password: str, name: str, student_id: str, phone: str) -> Tuple[bool, Optional[Dict]]:
        """学生注册"""
        # 验证注册信息
        valid, error = self._validate_student_register(username, password, name, student_id, phone)
        if not valid:
            return False, {"error": error}
        
        # 注册用户
        db = next(get_db())
        try:
            # 创建新用户
            new_user = User(
                user_name=username,
                password_hash=self._hash_password(password),
                role="student",
                name=name,
                student_id=student_id,
                phone=phone
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            # 注册成功后自动登录
            login_success, login_result = login_service.authenticate(username, password)
            if login_success:
                return True, {
                    "username": username,
                    "role": "student",
                    "name": name,
                    "student_id": student_id,
                    "phone": phone,
                    "session_id": login_result.get("session_id"),
                    "user": login_result.get("user")
                }
            else:
                return True, {
                    "username": username,
                    "role": "student",
                    "name": name,
                    "student_id": student_id,
                    "phone": phone
                }
        except Exception as e:
            db.rollback()
            print(f"学生注册失败: {str(e)}")
            return False, {"error": "注册失败，请稍后重试"}
        finally:
            db.close()
    
    def register_teacher(self, username: str, password: str, name: str, teacher_id: str, phone: str) -> Tuple[bool, Optional[Dict]]:
        """教师注册"""
        # 验证注册信息
        valid, error = self._validate_teacher_register(username, password, name, teacher_id, phone)
        if not valid:
            return False, {"error": error}
        
        # 注册用户
        db = next(get_db())
        try:
            # 创建新用户
            new_user = User(
                user_name=username,
                password_hash=self._hash_password(password),
                role="teacher",
                name=name,
                teacher_id=teacher_id,
                phone=phone
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            # 注册成功后自动登录
            login_success, login_result = login_service.authenticate(username, password)
            if login_success:
                return True, {
                    "username": username,
                    "role": "teacher",
                    "name": name,
                    "teacher_id": teacher_id,
                    "phone": phone,
                    "session_id": login_result.get("session_id"),
                    "user": login_result.get("user")
                }
            else:
                return True, {
                    "username": username,
                    "role": "teacher",
                    "name": name,
                    "teacher_id": teacher_id,
                    "phone": phone
                }
        except Exception as e:
            db.rollback()
            print(f"教师注册失败: {str(e)}")
            return False, {"error": "注册失败，请稍后重试"}
        finally:
            db.close()

# 单例模式
register_service = RegisterService()