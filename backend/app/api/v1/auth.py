from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.services.Login import login_service
from app.services.Register import register_service
from app.services.ForgetPassword import forget_password_service

router = APIRouter(prefix="/api/v1", tags=["auth"])

class LoginRequest(BaseModel):
    identifier: str
    password: str

class RegisterStudentRequest(BaseModel):
    username: str
    password: str
    name: str
    student_id: str
    phone: str

class RegisterTeacherRequest(BaseModel):
    username: str
    password: str
    name: str
    teacher_id: str
    phone: str

class VerificationCodeRequest(BaseModel):
    phone: str

class VerifyCodeRequest(BaseModel):
    phone: str
    code: str

class ResetPasswordRequest(BaseModel):
    phone: str
    new_password: str

@router.post("/login")
async def login(request: LoginRequest):
    """用户登录"""
    success, result = login_service.authenticate(request.identifier, request.password)
    if not success:
        raise HTTPException(status_code=401, detail=result.get("error"))
    return result

@router.post("/register/student")
async def register_student(request: RegisterStudentRequest):
    """学生注册"""
    success, result = register_service.register_student(
        request.username,
        request.password,
        request.name,
        request.student_id,
        request.phone
    )
    if not success:
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@router.post("/register/teacher")
async def register_teacher(request: RegisterTeacherRequest):
    """教师注册"""
    success, result = register_service.register_teacher(
        request.username,
        request.password,
        request.name,
        request.teacher_id,
        request.phone
    )
    if not success:
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@router.post("/register/send-code")
async def send_verification_code(request: VerificationCodeRequest):
    """发送验证码"""
    success, message = register_service.send_verification_code(request.phone)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}

@router.post("/register/verify-code")
async def verify_verification_code(request: VerifyCodeRequest):
    """验证验证码"""
    success, message = register_service.verify_verification_code(request.phone, request.code)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}

@router.post("/forget/send-code")
async def send_forget_verification_code(request: VerificationCodeRequest):
    """发送忘记密码验证码"""
    success, message = forget_password_service.send_verification_code(request.phone)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}

@router.post("/forget/verify-code")
async def verify_forget_verification_code(request: VerifyCodeRequest):
    """验证忘记密码验证码"""
    success, message = forget_password_service.verify_verification_code(request.phone, request.code)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}

@router.post("/forget/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """重置密码（无需验证码）"""
    # 直接重置密码
    success, message = forget_password_service.reset_password(request.phone, request.new_password)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {"message": message}
