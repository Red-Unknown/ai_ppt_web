from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional
from app.services.Login import login_service

router = APIRouter(prefix="/api/v1/login", tags=["login"])

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

@router.post("/", response_model=LoginResponse)
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
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/logout", response_model=LoginResponse)
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
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate", response_model=LoginResponse)
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
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{username}", response_model=LoginResponse)
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
        raise HTTPException(status_code=500, detail=str(e))
