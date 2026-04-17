"""
认证服务
提供用户认证和权限检查功能
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict
import jwt
from datetime import datetime, timedelta

try:
    from backend.app.core.config import settings
except ImportError:
    from app.core.config import settings

# JWT配置
SECRET_KEY = getattr(settings, 'SECRET_KEY', 'your-secret-key-here')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 1

security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建JWT访问令牌
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict]:
    """
    解码JWT令牌
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict:
    """
    获取当前用户（JWT认证）
    
    从请求头中提取并验证JWT令牌
    """
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    role = payload.get("role")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "user_id": user_id,
        "role": role,
        "email": payload.get("email"),
        "name": payload.get("name")
    }


def require_teacher(
    current_user: Dict = Depends(get_current_user)
) -> Dict:
    """
    要求教师权限
    
    检查当前用户是否为教师角色
    """
    if current_user.get("role") != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要教师权限"
        )
    return current_user


def require_student(
    current_user: Dict = Depends(get_current_user)
) -> Dict:
    """
    要求学生权限
    
    检查当前学生是否为学生角色
    """
    if current_user.get("role") != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要学生权限"
        )
    return current_user


# 模拟用户数据库（实际项目中应该使用真实的数据库）
MOCK_USERS = {
    "teacher@example.com": {
        "user_id": "teacher_001",
        "email": "teacher@example.com",
        "name": "张老师",
        "role": "teacher",
        "password": "hashed_password"
    },
    "student@example.com": {
        "user_id": "student_001",
        "email": "student@example.com",
        "name": "李同学",
        "role": "student",
        "password": "hashed_password"
    }
}


def authenticate_user(email: str, password: str) -> Optional[Dict]:
    """
    验证用户凭据
    
    实际项目中应该查询数据库并验证密码
    """
    user = MOCK_USERS.get(email)
    if user and user["password"] == "hashed_password":  # 简化验证
        return {
            "user_id": user["user_id"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"]
        }
    return None


def get_user_by_id(user_id: str) -> Optional[Dict]:
    """
    根据用户ID获取用户信息
    """
    for user in MOCK_USERS.values():
        if user["user_id"] == user_id:
            return {
                "user_id": user["user_id"],
                "email": user["email"],
                "name": user["name"],
                "role": user["role"]
            }
    return None
