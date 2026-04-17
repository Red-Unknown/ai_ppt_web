"""
第三模块：课程 API
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

try:
    from backend.app.core.database import get_db
    from backend.app.models.subject import Subject, Chapter
    from backend.app.models.course_new import Course, Slide, CourseDocument
    from backend.app.schemas.course_new import (
        CourseCreate, CourseUpdate, CourseResponse, CourseDetailResponse,
        CourseWithRelations, SlideResponse, CourseDocumentResponse
    )
    from backend.app.services.auth_service import get_current_user, require_teacher
except ImportError:
    from app.core.database import get_db
    from app.models.subject import Subject, Chapter
    from app.models.course_new import Course, Slide, CourseDocument
    from app.schemas.course_new import (
        CourseCreate, CourseUpdate, CourseResponse, CourseDetailResponse,
        CourseWithRelations, SlideResponse, CourseDocumentResponse
    )
    from app.services.auth_service import get_current_user, require_teacher

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("", response_model=List[CourseResponse])
def get_courses(
    role: Optional[str] = Query(None, description="用户角色过滤"),
    subject_id: Optional[int] = Query(None, gt=0, description="科目ID过滤"),
    chapter_id: Optional[int] = Query(None, gt=0, description="章节ID过滤"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    获取课程列表
    
    - role: 可选，'student' 或 'teacher' 进行过滤
    - subject_id: 可选，按科目过滤
    - chapter_id: 可选，按章节过滤
    """
    query = db.query(Course)
    
    if subject_id:
        query = query.filter(Course.subject_id == subject_id)
    if chapter_id:
        query = query.filter(Course.chapter_id == chapter_id)
    
    courses = query.all()
    return courses


@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(
    course: CourseCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_teacher)
):
    """
    创建课程（仅教师）
    """
    # 验证科目是否存在
    subject = db.query(Subject).filter(Subject.id == course.subject_id).first()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="科目不存在"
        )
    
    # 验证章节是否存在
    chapter = db.query(Chapter).filter(
        Chapter.id == course.chapter_id,
        Chapter.subject_id == course.subject_id
    ).first()
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="章节不存在或不属于该科目"
        )
    
    db_course = Course(
        title=course.title,
        description=course.description,
        subject_id=course.subject_id,
        chapter_id=course.chapter_id
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


@router.get("/{course_id}", response_model=CourseWithRelations)
def get_course_detail(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    获取课程详情
    """
    db_course = db.query(Course).filter(Course.id == course_id).first()
    if not db_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="课程不存在"
        )
    
    # 计算幻灯片数量
    slide_count = db.query(Slide).filter(Slide.course_id == course_id).count()
    
    # 构建响应
    response_data = {
        **db_course.__dict__,
        "slide_count": slide_count,
        "slides": db_course.slides,
        "documents": db_course.documents
    }
    
    return response_data


@router.put("/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: int,
    course: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_teacher)
):
    """
    更新课程（仅教师）
    """
    db_course = db.query(Course).filter(Course.id == course_id).first()
    if not db_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="课程不存在"
        )
    
    if course.title is not None:
        db_course.title = course.title
    if course.description is not None:
        db_course.description = course.description
    
    db.commit()
    db.refresh(db_course)
    return db_course


@router.delete("/{course_id}")
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_teacher)
):
    """
    删除课程（仅教师）
    """
    db_course = db.query(Course).filter(Course.id == course_id).first()
    if not db_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="课程不存在"
        )
    
    db.delete(db_course)
    db.commit()
    return {"message": "课程删除成功"}


@router.get("/{course_id}/slides", response_model=List[SlideResponse])
def get_course_slides(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    获取课程的幻灯片列表
    """
    # 验证课程是否存在
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="课程不存在"
        )
    
    slides = db.query(Slide).filter(
        Slide.course_id == course_id
    ).order_by(Slide.slide_index).all()
    
    return slides


@router.get("/{course_id}/documents", response_model=List[CourseDocumentResponse])
def get_course_documents(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    获取课程的文档列表
    """
    # 验证课程是否存在
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="课程不存在"
        )
    
    documents = db.query(CourseDocument).filter(
        CourseDocument.course_id == course_id
    ).all()
    
    return documents
