"""
第二模块：科目与章节 API
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

try:
    from backend.app.core.database import get_db
    from backend.app.models.subject import Subject, Chapter
    from backend.app.schemas.subject import (
        SubjectCreate, SubjectUpdate, SubjectResponse,
        ChapterCreate, ChapterUpdate, ChapterResponse, ChapterWithSubject
    )
    from backend.app.services.auth_service import get_current_user, require_teacher
except ImportError:
    from app.core.database import get_db
    from app.models.subject import Subject, Chapter
    from app.schemas.subject import (
        SubjectCreate, SubjectUpdate, SubjectResponse,
        ChapterCreate, ChapterUpdate, ChapterResponse, ChapterWithSubject
    )
    from app.services.auth_service import get_current_user, require_teacher

router = APIRouter(prefix="/subjects", tags=["subjects"])
chapter_router = APIRouter(prefix="/chapters", tags=["chapters"])


# ==================== Subject Endpoints ====================

@router.get("", response_model=List[SubjectResponse])
def get_subjects(
    role: Optional[str] = Query(None, description="用户角色过滤"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    获取科目列表
    
    - role: 可选，'student' 或 'teacher' 进行过滤
    """
    query = db.query(Subject)
    subjects = query.all()
    return subjects


@router.post("", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
def create_subject(
    subject: SubjectCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_teacher)
):
    """
    创建科目（仅教师）
    """
    db_subject = Subject(name=subject.name)
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject


@router.put("/{subject_id}", response_model=SubjectResponse)
def update_subject(
    subject_id: int,
    subject: SubjectUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_teacher)
):
    """
    更新科目（仅教师）
    """
    db_subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not db_subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="科目不存在"
        )
    
    if subject.name is not None:
        db_subject.name = subject.name
    
    db.commit()
    db.refresh(db_subject)
    return db_subject


@router.delete("/{subject_id}")
def delete_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_teacher)
):
    """
    删除科目（仅教师）
    """
    db_subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not db_subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="科目不存在"
        )
    
    db.delete(db_subject)
    db.commit()
    return {"message": "科目删除成功"}


# ==================== Chapter Endpoints ====================

@chapter_router.get("", response_model=List[ChapterResponse])
def get_chapters(
    subject_id: int = Query(..., gt=0, description="科目ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    获取章节列表
    
    - subject_id: 必填，所属科目ID
    """
    # 验证科目是否存在
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="科目不存在"
        )
    
    chapters = db.query(Chapter).filter(
        Chapter.subject_id == subject_id
    ).order_by(Chapter.order).all()
    
    return chapters


@chapter_router.post("", response_model=ChapterResponse, status_code=status.HTTP_201_CREATED)
def create_chapter(
    chapter: ChapterCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_teacher)
):
    """
    创建章节（仅教师）
    """
    # 验证科目是否存在
    subject = db.query(Subject).filter(Subject.id == chapter.subject_id).first()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="科目不存在"
        )
    
    db_chapter = Chapter(
        subject_id=chapter.subject_id,
        name=chapter.name,
        order=chapter.order
    )
    db.add(db_chapter)
    db.commit()
    db.refresh(db_chapter)
    return db_chapter


@chapter_router.put("/{chapter_id}", response_model=ChapterResponse)
def update_chapter(
    chapter_id: int,
    chapter: ChapterUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_teacher)
):
    """
    更新章节（仅教师）
    """
    db_chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not db_chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="章节不存在"
        )
    
    if chapter.name is not None:
        db_chapter.name = chapter.name
    if chapter.order is not None:
        db_chapter.order = chapter.order
    
    db.commit()
    db.refresh(db_chapter)
    return db_chapter


@chapter_router.delete("/{chapter_id}")
def delete_chapter(
    chapter_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_teacher)
):
    """
    删除章节（仅教师）
    """
    db_chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not db_chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="章节不存在"
        )
    
    db.delete(db_chapter)
    db.commit()
    return {"message": "章节删除成功"}
