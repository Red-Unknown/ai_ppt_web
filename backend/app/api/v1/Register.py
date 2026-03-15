from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.Register import register_service

router = APIRouter(prefix="/api/v1/register", tags=["register"])

class StudentRegisterRequest(BaseModel):
    username: str
    password: str
    name: str
    student_id: str
    phone: str
    code: str

class TeacherRegisterRequest(BaseModel):
    username: str
    password: str
    name: str
    teacher_id: str
    phone: str
    code: str

class RegisterResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
    error: Optional[str] = None

class SendCodeRequest(BaseModel):
    phone: str

class VerifyCodeRequest(BaseModel):
    phone: str
    code: str

class CheckPasswordRequest(BaseModel):
    password: str

@router.post("/send-code", response_model=RegisterResponse)
async def send_verification_code(request: SendCodeRequest):
    """发送验证码接口"""
    try:
        success, message = register_service.send_verification_code(request.phone)
        if success:
            return RegisterResponse(
                success=True,
                message=message
            )
        else:
            return RegisterResponse(
                success=False,
                message="发送验证码失败",
                error=message
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verify-code", response_model=RegisterResponse)
async def verify_verification_code(request: VerifyCodeRequest):
    """验证验证码接口"""
    try:
        success, message = register_service.verify_verification_code(request.phone, request.code)
        if success:
            return RegisterResponse(
                success=True,
                message=message
            )
        else:
            return RegisterResponse(
                success=False,
                message="验证验证码失败",
                error=message
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/check-password", response_model=RegisterResponse)
async def check_password_strength(request: CheckPasswordRequest):
    """检查密码强度接口"""
    try:
        result = register_service.check_password_strength(request.password)
        return RegisterResponse(
            success=True,
            message="检查密码强度成功",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/student", response_model=RegisterResponse)
async def register_student(request: StudentRegisterRequest):
    """学生注册接口"""
    try:
        # 验证验证码
        code_valid, code_message = register_service.verify_verification_code(request.phone, request.code)
        if not code_valid:
            return RegisterResponse(
                success=False,
                message="验证码验证失败",
                error=code_message
            )
        
        success, result = register_service.register_student(
            request.username, 
            request.password, 
            request.name,
            request.student_id,
            request.phone
        )
        if success:
            return RegisterResponse(
                success=True,
                message="学生注册成功",
                data=result
            )
        else:
            return RegisterResponse(
                success=False,
                message="学生注册失败",
                error=result.get("error", "未知错误")
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/teacher", response_model=RegisterResponse)
async def register_teacher(request: TeacherRegisterRequest):
    """教师注册接口"""
    try:
        # 验证验证码
        code_valid, code_message = register_service.verify_verification_code(request.phone, request.code)
        if not code_valid:
            return RegisterResponse(
                success=False,
                message="验证码验证失败",
                error=code_message
            )
        
        success, result = register_service.register_teacher(
            request.username, 
            request.password, 
            request.name,
            request.teacher_id,
            request.phone
        )
        if success:
            return RegisterResponse(
                success=True,
                message="教师注册成功",
                data=result
            )
        else:
            return RegisterResponse(
                success=False,
                message="教师注册失败",
                error=result.get("error", "未知错误")
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))