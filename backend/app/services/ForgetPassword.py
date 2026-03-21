from typing import Dict, Optional, Tuple
import re
import random
import time
import os
import bcrypt
from sqlalchemy.orm import Session
from app.core.database import get_db, User
import logging

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs', 'forget_password.log')),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)

class ForgetPasswordService:
    def __init__(self):
        # 存储验证码（暂时使用内存存储）
        self.verification_codes = {}
        self.code_expiry = 300  # 5分钟过期
    
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
            logger.error(f"验证验证码失败: {str(e)}")
            return False, f"验证验证码失败: {str(e)}"
    
    def reset_password(self, phone: str, new_password: str) -> Tuple[bool, Optional[str]]:
        """重置密码（无需验证码）"""
        # 验证手机号格式
        if not re.match(r'^1[3-9]\d{9}$', phone):
            return False, "手机号格式不正确"
        
        # 验证密码强度
        if len(new_password) < 8 or len(new_password) > 16:
            return False, "密码长度应在8-16位之间"
        
        if not any(char.isdigit() for char in new_password) or not any(char.isalpha() for char in new_password):
            return False, "密码至少包含数字和字母两种元素"
        
        # 重置密码
        db = next(get_db())
        try:
            user = db.query(User).filter(User.phone == phone).first()
            if not user:
                return False, "该手机号未注册"
            
            # 密码加密
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            user.password_hash = hashed_password.decode('utf-8')
            
            db.commit()
            db.refresh(user)
            
            logger.info(f"密码重置成功: {phone}")
            return True, "密码重置成功"
        except Exception as e:
            db.rollback()
            logger.error(f"重置密码失败: {str(e)}")
            return False, "重置密码失败，请稍后重试"
        finally:
            db.close()

# 单例模式
forget_password_service = ForgetPasswordService()