from typing import Dict, Optional, Tuple
import hashlib
import time

class LoginService:
    def __init__(self):
        # 内存数据结构模拟数据库
        self.users = {
            "admin": {
                "password": self._hash_password("admin123"),
                "role": "teacher",
                "name": "管理员"
            },
            "student1": {
                "password": self._hash_password("student123"),
                "role": "student",
                "name": "学生1"
            }
        }
        # 会话存储
        self.sessions = {}
        self.session_timeout = 3600  # 1小时
    
    def _hash_password(self, password: str) -> str:
        """密码哈希处理"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _generate_session_id(self, username: str) -> str:
        """生成会话ID"""
        return hashlib.sha256(f"{username}_{time.time()}".encode()).hexdigest()
    
    def authenticate(self, username: str, password: str) -> Tuple[bool, Optional[Dict]]:
        """用户身份验证"""
        if username not in self.users:
            return False, {"error": "用户名不存在"}
        
        if self.users[username]["password"] != self._hash_password(password):
            return False, {"error": "密码错误"}
        
        # 生成会话
        session_id = self._generate_session_id(username)
        self.sessions[session_id] = {
            "username": username,
            "role": self.users[username]["role"],
            "name": self.users[username]["name"],
            "created_at": time.time()
        }
        
        return True, {
            "session_id": session_id,
            "user": {
                "username": username,
                "role": self.users[username]["role"],
                "name": self.users[username]["name"]
            }
        }
    
    def validate_session(self, session_id: str) -> Tuple[bool, Optional[Dict]]:
        """验证会话有效性"""
        if session_id not in self.sessions:
            return False, {"error": "会话不存在"}
        
        session = self.sessions[session_id]
        if time.time() - session["created_at"] > self.session_timeout:
            del self.sessions[session_id]
            return False, {"error": "会话已过期"}
        
        # 更新会话时间
        session["created_at"] = time.time()
        return True, session
    
    def logout(self, session_id: str) -> bool:
        """用户登出"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        """获取用户信息"""
        if username in self.users:
            return {
                "username": username,
                "role": self.users[username]["role"],
                "name": self.users[username]["name"]
            }
        return None

# 单例模式
login_service = LoginService()
