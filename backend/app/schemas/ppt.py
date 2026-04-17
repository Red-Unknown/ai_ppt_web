"""
PPT/图片上传 Schema
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


class SlideInfo(BaseModel):
    """幻灯片信息 Schema"""
    index: int = Field(..., ge=0, description="幻灯片索引")
    image_url: str = Field(..., description="图片URL")
    text: Optional[str] = Field(None, description="幻灯片文本内容")


class PPTBase(BaseModel):
    """PPT基础 Schema"""
    file_name: str = Field(..., min_length=1, max_length=255, description="文件名")


class PPTCreate(BaseModel):
    """创建PPT Schema"""
    course_id: int = Field(..., gt=0, description="所属课程ID")
    file_name: str = Field(..., min_length=1, max_length=255, description="文件名")
    file_path: Optional[str] = Field(None, max_length=500, description="文件存储路径")
    file_size: Optional[int] = Field(None, ge=0, description="文件大小(字节)")
    file_type: Optional[str] = Field(None, max_length=50, description="文件类型")


class PPTUpdate(BaseModel):
    """更新PPT Schema"""
    slide_count: Optional[int] = Field(None, ge=0, description="幻灯片数量")
    slides: Optional[List[Any]] = Field(None, description="幻灯片列表信息")
    parse_status: Optional[str] = Field(None, max_length=20, description="解析状态")


class PPTResponse(BaseModel):
    """PPT响应 Schema"""
    id: int
    course_id: int
    file_name: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    slide_count: int
    slides: Optional[List[Any]] = None
    parse_status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PPTUploadResponse(BaseModel):
    """PPT上传响应 Schema"""
    id: int
    course_id: int
    file_name: str
    slides: List[Any] = []
    message: str = "PPT上传成功"


class PPTParseResponse(BaseModel):
    """PPT解析响应 Schema"""
    id: int
    slides: List[Any]
    message: str = "PPT解析成功"


class PPTDeleteResponse(BaseModel):
    """PPT删除响应 Schema"""
    message: str = "PPT删除成功"
