"""
第四模块：PPT/图片上传 API
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
import uuid
from pathlib import Path

try:
    from backend.app.core.database import get_db
    from backend.app.core.config import settings
    from backend.app.models.course_new import Course, Slide
    from backend.app.models.ppt import PPT
    from backend.app.schemas.ppt import (
        PPTResponse, PPTUploadResponse, PPTParseResponse, PPTDeleteResponse
    )
    from backend.app.services.auth_service import require_teacher
except ImportError:
    from app.core.database import get_db
    from app.core.config import settings
    from app.models.course_new import Course, Slide
    from app.models.ppt import PPT
    from app.schemas.ppt import (
        PPTResponse, PPTUploadResponse, PPTParseResponse, PPTDeleteResponse
    )
    from app.services.auth_service import require_teacher

router = APIRouter(prefix="/ppts", tags=["ppts"])

# 配置上传目录
UPLOAD_DIR = Path(settings.BASE_DIR) / "uploads" / "ppts"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# 允许的文件类型
ALLOWED_EXTENSIONS = {'.ppt', '.pptx', '.pdf', '.png', '.jpg', '.jpeg'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


def get_file_extension(filename: str) -> str:
    """获取文件扩展名"""
    return Path(filename).suffix.lower()


def is_allowed_file(filename: str) -> bool:
    """检查文件类型是否允许"""
    return get_file_extension(filename) in ALLOWED_EXTENSIONS


@router.post("", response_model=PPTUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_ppt(
    course_id: int = Form(..., gt=0, description="所属课程ID"),
    file: UploadFile = File(..., description="PPT/图片文件"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_teacher)
):
    """
    上传PPT/图片（仅教师）
    
    支持格式: .ppt, .pptx, .pdf, .png, .jpg, .jpeg
    最大文件大小: 50MB
    """
    # 验证课程是否存在
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="课程不存在"
        )
    
    # 验证文件类型
    if not is_allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件格式。允许格式: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # 读取文件内容
    content = await file.read()
    
    # 验证文件大小
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件大小超过限制。最大允许: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # 生成唯一文件名
    file_ext = get_file_extension(file.filename)
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename
    
    # 保存文件
    with open(file_path, "wb") as buffer:
        buffer.write(content)
    
    # 创建数据库记录
    db_ppt = PPT(
        course_id=course_id,
        file_name=file.filename,
        file_path=str(file_path),
        file_size=len(content),
        file_type=file_ext,
        parse_status="pending"
    )
    db.add(db_ppt)
    db.commit()
    db.refresh(db_ppt)
    
    return {
        "id": db_ppt.id,
        "course_id": db_ppt.course_id,
        "file_name": db_ppt.file_name,
        "slides": [],
        "message": "PPT上传成功"
    }


@router.get("/{ppt_id}", response_model=PPTResponse)
def get_ppt(
    ppt_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_teacher)
):
    """
    获取PPT信息（仅教师）
    """
    db_ppt = db.query(PPT).filter(PPT.id == ppt_id).first()
    if not db_ppt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PPT不存在"
        )
    
    return db_ppt


@router.post("/{ppt_id}/parse", response_model=PPTParseResponse)
async def parse_ppt(
    ppt_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_teacher)
):
    """
    解析PPT/图片（仅教师）
    
    将PPT转换为幻灯片列表，并提取内容
    """
    db_ppt = db.query(PPT).filter(PPT.id == ppt_id).first()
    if not db_ppt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PPT不存在"
        )
    
    # 更新解析状态
    db_ppt.parse_status = "parsing"
    db.commit()
    
    try:
        slides_info = []
        file_ext = get_file_extension(db_ppt.file_name)
        
        if file_ext in {'.png', '.jpg', '.jpeg'}:
            # 图片文件：作为单张幻灯片处理
            slide = Slide(
                course_id=db_ppt.course_id,
                slide_index=0,
                image_url=f"/uploads/ppts/{Path(db_ppt.file_path).name}",
                duration=5
            )
            db.add(slide)
            
            slides_info.append({
                "index": 0,
                "image_url": f"/uploads/ppts/{Path(db_ppt.file_path).name}",
                "text": ""
            })
            
            db_ppt.slide_count = 1
            
        elif file_ext in {'.ppt', '.pptx', '.pdf'}:
            # PPT/PDF文件：这里简化处理，实际需要专门的解析库
            # 如: python-pptx, PyPDF2 等
            # 这里仅作为示例，创建占位幻灯片
            
            # TODO: 实现实际的PPT/PDF解析逻辑
            # 可以使用:
            # - python-pptx: 解析 .pptx 文件
            # - pdf2image: 将PDF转换为图片
            # - Pillow: 处理图片
            
            # 示例：创建一张占位幻灯片
            slide = Slide(
                course_id=db_ppt.course_id,
                slide_index=0,
                image_url=f"/uploads/ppts/{Path(db_ppt.file_path).name}",
                duration=10,
                content=f"PPT文件: {db_ppt.file_name}"
            )
            db.add(slide)
            
            slides_info.append({
                "index": 0,
                "image_url": f"/uploads/ppts/{Path(db_ppt.file_path).name}",
                "text": f"PPT文件: {db_ppt.file_name}"
            })
            
            db_ppt.slide_count = 1
        
        db_ppt.slides = slides_info
        db_ppt.parse_status = "completed"
        db.commit()
        db.refresh(db_ppt)
        
        return {
            "id": db_ppt.id,
            "slides": slides_info,
            "message": "PPT解析成功"
        }
        
    except Exception as e:
        db_ppt.parse_status = "failed"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PPT解析失败: {str(e)}"
        )


@router.delete("/{ppt_id}", response_model=PPTDeleteResponse)
def delete_ppt(
    ppt_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_teacher)
):
    """
    删除PPT/图片（仅教师）
    """
    db_ppt = db.query(PPT).filter(PPT.id == ppt_id).first()
    if not db_ppt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PPT不存在"
        )
    
    # 删除物理文件
    try:
        if os.path.exists(db_ppt.file_path):
            os.remove(db_ppt.file_path)
    except Exception as e:
        # 记录错误但不阻止数据库记录删除
        print(f"删除文件失败: {e}")
    
    # 删除关联的幻灯片记录
    db.query(Slide).filter(Slide.course_id == db_ppt.course_id).delete()
    
    # 删除数据库记录
    db.delete(db_ppt)
    db.commit()
    
    return {"message": "PPT删除成功"}


@router.get("", response_model=List[PPTResponse])
def list_ppts(
    course_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_teacher)
):
    """
    获取PPT列表（仅教师）
    
    - course_id: 可选，按课程过滤
    """
    query = db.query(PPT)
    
    if course_id:
        query = query.filter(PPT.course_id == course_id)
    
    ppts = query.order_by(PPT.created_at.desc()).all()
    return ppts
