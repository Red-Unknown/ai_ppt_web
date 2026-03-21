from typing import Dict, Optional, Tuple
import hashlib
import time
import os
import re
import logging
import bcrypt
from sqlalchemy.orm import Session
from app.core.database import get_db, User

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs', 'login.log')),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)

class LoginService:
    def __init__(self):
        self.session_timeout = 3600  # 1小时
        self.login_attempts = {}  # 防暴力破解：记录登录尝试次数
        self.max_attempts = 5  # 最大尝试次数
        self.lockout_time = 300  # 锁定时间（5分钟）
    
    def _hash_password(self, password: str) -> str:
        """密码哈希处理"""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    def _verify_password(self, password: str, hashed_password: str) -> bool:
        """验证密码"""
        return bcrypt.checkpw(password.encode(), hashed_password.encode())
    
    def _generate_session_id(self, username: str) -> str:
        """生成会话ID"""
        return hashlib.sha256(f"{username}_{time.time()}_{os.urandom(16).hex()}".encode()).hexdigest()
    
    def _validate_input(self, identifier: str, password: str) -> Tuple[bool, Optional[str]]:
        """验证输入"""
        # 验证标识符（用户名/学号/手机号）
        if not identifier or len(identifier) > 50:
            return False, "账号长度无效"
        
        # 验证密码
        if not password or len(password) < 6 or len(password) > 100:
            return False, "密码长度无效"
        
        # 检查是否包含特殊字符（防止注入）
        if re.search(r'[<>"\'&;]', identifier) or re.search(r'[<>"\'&;]', password):
            return False, "输入包含无效字符"
        
        return True, None
    
    def _check_login_attempts(self, identifier: str) -> Tuple[bool, Optional[str]]:
        """检查登录尝试次数"""
        if identifier in self.login_attempts:
            attempt_info = self.login_attempts[identifier]
            if attempt_info['attempts'] >= self.max_attempts:
                if time.time() - attempt_info['last_attempt'] < self.lockout_time:
                    return False, f"账号已被锁定，请{self.lockout_time//60}分钟后重试"
                else:
                    # 锁定时间已过，重置尝试次数
                    del self.login_attempts[identifier]
        return True, None
    
    def _record_login_attempt(self, identifier: str, success: bool):
        """记录登录尝试"""
        if not success:
            if identifier not in self.login_attempts:
                self.login_attempts[identifier] = {
                    'attempts': 0,
                    'last_attempt': time.time()
                }
            self.login_attempts[identifier]['attempts'] += 1
            self.login_attempts[identifier]['last_attempt'] = time.time()
        else:
            # 登录成功，清除尝试记录
            if identifier in self.login_attempts:
                del self.login_attempts[identifier]
    
    def authenticate(self, identifier: str, password: str) -> Tuple[bool, Optional[Dict]]:
        """用户身份验证
        identifier: 可以是用户名、学号、手机号
        """
        # 验证输入
        valid, error = self._validate_input(identifier, password)
        if not valid:
            logger.warning(f"登录输入验证失败: {error}")
            return False, {"error": error}
        
        # 检查登录尝试次数
        valid, error = self._check_login_attempts(identifier)
        if not valid:
            logger.warning(f"登录尝试次数过多: {identifier}")
            return False, {"error": error}
        
        # 查找用户
        db = next(get_db())
        user = None
        
        try:
            # 首先尝试通过用户名查找
            user = db.query(User).filter(User.user_name == identifier).first()
            
            # 尝试通过学号查找
            if not user:
                user = db.query(User).filter(User.student_id == identifier).first()
            
            # 尝试通过手机号查找
            if not user:
                user = db.query(User).filter(User.phone == identifier).first()
            
            if not user:
                self._record_login_attempt(identifier, False)
                logger.warning(f"用户不存在: {identifier}")
                return False, {"error": "用户不存在"}
            
            if not self._verify_password(password, user.password_hash):
                self._record_login_attempt(identifier, False)
                logger.warning(f"密码错误: {identifier}")
                return False, {"error": "密码错误"}
            
            # 登录成功，记录尝试
            self._record_login_attempt(identifier, True)
            
            # 生成会话
            session_id = self._generate_session_id(user.user_name)
            
            # 保存会话到内存（暂时使用内存存储，后续可考虑数据库存储）
            if not hasattr(self, 'sessions'):
                self.sessions = {}
            
            self.sessions[session_id] = {
                "username": user.user_name,
                "role": user.role,
                "name": user.name,
                "created_at": time.time(),
                "last_access": time.time()
            }
            
            # 记录登录成功
            logger.info(f"登录成功: {user.user_name}, 角色: {user.role}")
            
            return True, {
                "session_id": session_id,
                "user": {
                    "username": user.user_name,
                    "role": user.role,
                    "name": user.name
                }
            }
        except Exception as e:
            logger.error(f"登录数据库操作失败: {str(e)}")
            return False, {"error": "登录失败，请稍后重试"}
        finally:
            db.close()
    
    def validate_session(self, session_id: str) -> Tuple[bool, Optional[Dict]]:
        """验证会话有效性"""
        if not session_id:
            return False, {"error": "会话ID不能为空"}
        
        if not hasattr(self, 'sessions'):
            self.sessions = {}
        
        if session_id not in self.sessions:
            logger.warning(f"会话不存在: {session_id}")
            return False, {"error": "会话不存在"}
        
        session = self.sessions[session_id]
        if time.time() - session["created_at"] > self.session_timeout:
            del self.sessions[session_id]
            logger.warning(f"会话已过期: {session_id}")
            return False, {"error": "会话已过期"}
        
        # 更新会话时间
        session["last_access"] = time.time()
        
        return True, session
    
    def logout(self, session_id: str) -> bool:
        """用户登出"""
        if not hasattr(self, 'sessions'):
            self.sessions = {}
        
        if session_id in self.sessions:
            username = self.sessions[session_id].get("username")
            del self.sessions[session_id]
            logger.info(f"登出成功: {username}")
            return True
        logger.warning(f"登出失败: 会话不存在 {session_id}")
        return False
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        """获取用户信息"""
        db = next(get_db())
        try:
            user = db.query(User).filter(User.user_name == username).first()
            if user:
                return {
                    "username": user.user_name,
                    "role": user.role,
                    "name": user.name,
                    "student_id": user.student_id,
                    "teacher_id": user.teacher_id,
                    "phone": user.phone
                }
            return None
        except Exception as e:
            logger.error(f"获取用户信息失败: {str(e)}")
            return None
        finally:
            db.close()
    
    def cleanup_expired_sessions(self):
        """清理过期会话"""
        if not hasattr(self, 'sessions'):
            self.sessions = {}
        
        expired_sessions = []
        current_time = time.time()
        
        for session_id, session in self.sessions.items():
            if current_time - session["created_at"] > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
        
        if expired_sessions:
            logger.info(f"清理过期会话: {len(expired_sessions)} 个")

# 单例模式
login_service = LoginService()
