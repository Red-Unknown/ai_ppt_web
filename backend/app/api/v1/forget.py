from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.ForgetPassword import forget_password_service

router = APIRouter(prefix="/api/v1/forget", tags=["forget"])

class VerificationCodeRequest(BaseModel):
    phone: str

class VerifyCodeRequest(BaseModel):
    phone: str
    code: str

class ResetPasswordRequest(BaseModel):
    phone: str
    new_password: str

@router.post("/send-code")
async def send_forget_verification_code(request: VerificationCodeRequest):
    """发送忘记密码验证码"""
    success, message = forget_password_service.send_verification_code(request.phone)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}

@router.post("/verify-code")
async def verify_forget_verification_code(request: VerifyCodeRequest):
    """验证忘记密码验证码"""
    success, message = forget_password_service.verify_verification_code(request.phone, request.code)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """重置密码（无需验证码）"""
    # 直接重置密码
    success, message = forget_password_service.reset_password(request.phone, request.new_password)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {"message": message}