"""
课程 Schema
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


# ==================== Slide Schemas ====================

class SlideBase(BaseModel):
    """幻灯片基础 Schema"""
    slide_index: int = Field(..., ge=0, description="幻灯片顺序")
    image_url: Optional[str] = Field(None, max_length=500, description="图片URL")
    duration: int = Field(default=0, ge=0, description="显示时长(秒)")
    content: Optional[str] = Field(None, description="幻灯片内容")


class SlideCreate(SlideBase):
    """创建幻灯片 Schema"""
    pass


class SlideResponse(SlideBase):
    """幻灯片响应 Schema"""
    id: int
    course_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== CourseDocument Schemas ====================

class CourseDocumentBase(BaseModel):
    """课程文档基础 Schema"""
    title: str = Field(..., min_length=1, max_length=200, description="文档标题")
    content: Optional[str] = Field(None, description="文档内容")
    doc_type: str = Field(default="text", max_length=50, description="文档类型")


class CourseDocumentCreate(CourseDocumentBase):
    """创建课程文档 Schema"""
    pass


class CourseDocumentResponse(CourseDocumentBase):
    """课程文档响应 Schema"""
    id: int
    course_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== Course Schemas ====================

class CourseBase(BaseModel):
    """课程基础 Schema"""
    title: str = Field(..., min_length=1, max_length=200, description="课程标题")
    description: Optional[str] = Field(None, description="课程描述")


class CourseCreate(CourseBase):
    """创建课程 Schema"""
    subject_id: int = Field(..., gt=0, description="所属科目ID")
    chapter_id: int = Field(..., gt=0, description="所属章节ID")


class CourseUpdate(BaseModel):
    """更新课程 Schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="课程标题")
    description: Optional[str] = Field(None, description="课程描述")


class CourseResponse(CourseBase):
    """课程响应 Schema"""
    id: int
    subject_id: int
    chapter_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CourseDetailResponse(CourseResponse):
    """课程详情响应 Schema"""
    slide_count: int = Field(default=0, description="幻灯片数量")


class CourseWithRelations(CourseDetailResponse):
    """带关联数据的课程 Schema"""
    slides: List[SlideResponse] = []
    documents: List[CourseDocumentResponse] = []


# ==================== LessonPlan Schemas ====================

class LessonPlanBase(BaseModel):
    """教案基础 Schema"""
    content: Any = Field(..., description="教案内容")


class LessonPlanCreate(LessonPlanBase):
    """创建教案 Schema"""
    course_id: int = Field(..., gt=0, description="所属课程ID")


class LessonPlanUpdate(BaseModel):
    """更新教案 Schema"""
    content: Any = Field(..., description="教案内容")


class LessonPlanResponse(LessonPlanBase):
    """教案响应 Schema"""
    id: int
    course_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== AI Generate Schemas ====================

class AILessonPlanGenerateRequest(BaseModel):
    """AI生成教案请求 Schema"""
    course_id: int = Field(..., gt=0, description="课程ID")
    ppt_id: Optional[int] = Field(None, gt=0, description="PPT ID")


class AILessonPlanGenerateResponse(BaseModel):
    """AI生成教案响应 Schema"""
    id: int
    course_id: int
    content: Any
    created_at: datetime

    class Config:
        from_attributes = True
