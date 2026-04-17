"""
科目与章节 Schema
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ==================== Subject Schemas ====================

class SubjectBase(BaseModel):
    """科目基础 Schema"""
    name: str = Field(..., min_length=1, max_length=100, description="科目名称")


class SubjectCreate(SubjectBase):
    """创建科目 Schema"""
    pass


class SubjectUpdate(BaseModel):
    """更新科目 Schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="科目名称")


class SubjectResponse(SubjectBase):
    """科目响应 Schema"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Chapter Schemas ====================

class ChapterBase(BaseModel):
    """章节基础 Schema"""
    name: str = Field(..., min_length=1, max_length=100, description="章节名称")
    order: int = Field(default=0, ge=0, description="章节顺序")


class ChapterCreate(ChapterBase):
    """创建章节 Schema"""
    subject_id: int = Field(..., gt=0, description="所属科目ID")


class ChapterUpdate(BaseModel):
    """更新章节 Schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="章节名称")
    order: Optional[int] = Field(None, ge=0, description="章节顺序")


class ChapterResponse(ChapterBase):
    """章节响应 Schema"""
    id: int
    subject_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChapterWithSubject(ChapterResponse):
    """带科目信息的章节 Schema"""
    subject: Optional[SubjectResponse] = None
