from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Tuple
import hashlib
import time

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
    error: Optional[str] = None

class LogoutRequest(BaseModel):
    session_id: str

class ValidateSessionRequest(BaseModel):
    session_id: str

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

# 创建FastAPI应用
app = FastAPI(
    title="登录服务",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建登录服务实例
login_service = LoginService()

@app.post("/api/v1/login/", response_model=LoginResponse)
async def login(request: LoginRequest):
    """用户登录接口"""
    try:
        success, result = login_service.authenticate(request.username, request.password)
        if success:
            return LoginResponse(
                success=True,
                message="登录成功",
                data=result
            )
        else:
            return LoginResponse(
                success=False,
                message="登录失败",
                error=result.get("error", "未知错误")
            )
    except Exception as e:
        return LoginResponse(
            success=False,
            message="登录失败",
            error=str(e)
        )

@app.post("/api/v1/login/logout", response_model=LoginResponse)
async def logout(request: LogoutRequest):
    """用户登出接口"""
    try:
        success = login_service.logout(request.session_id)
        if success:
            return LoginResponse(
                success=True,
                message="登出成功"
            )
        else:
            return LoginResponse(
                success=False,
                message="登出失败",
                error="会话不存在"
            )
    except Exception as e:
        return LoginResponse(
            success=False,
            message="登出失败",
            error=str(e)
        )

@app.post("/api/v1/login/validate", response_model=LoginResponse)
async def validate_session(request: ValidateSessionRequest):
    """验证会话有效性接口"""
    try:
        success, result = login_service.validate_session(request.session_id)
        if success:
            return LoginResponse(
                success=True,
                message="会话有效",
                data=result
            )
        else:
            return LoginResponse(
                success=False,
                message="会话无效",
                error=result.get("error", "未知错误")
            )
    except Exception as e:
        return LoginResponse(
            success=False,
            message="验证失败",
            error=str(e)
        )

@app.get("/api/v1/login/user/{username}", response_model=LoginResponse)
async def get_user_info(username: str):
    """获取用户信息接口"""
    try:
        user_info = login_service.get_user_info(username)
        if user_info:
            return LoginResponse(
                success=True,
                message="获取用户信息成功",
                data=user_info
            )
        else:
            return LoginResponse(
                success=False,
                message="获取用户信息失败",
                error="用户不存在"
            )
    except Exception as e:
        return LoginResponse(
            success=False,
            message="获取用户信息失败",
            error=str(e)
        )

@app.get("/")
async def root():
    return {
        "message": "登录服务运行中",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": [
            "/api/v1/login/ (POST) - 用户登录",
            "/api/v1/login/logout (POST) - 用户登出",
            "/api/v1/login/validate (POST) - 验证会话",
            "/api/v1/login/user/{username} (GET) - 获取用户信息"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("login_server:app", host="0.0.0.0", port=8000, reload=True)
