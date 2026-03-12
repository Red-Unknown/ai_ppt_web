
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl

# --- Request Models ---
class ParseRequest(BaseModel):
    schoolId: str = Field(..., description="School ID")
    userId: str = Field(..., description="User ID (Teacher/User)")
    courseId: str = Field(..., description="Course ID")
    fileType: str = Field(..., description="File Type: 'ppt' or 'pdf'")
    fileUrl: str = Field(..., description="Courseware File URL")
    isExtractKeyPoint: bool = Field(True, description="Whether to extract key points")
    enc: str = Field(..., description="Signature")

# --- Response Models ---
class BoundingBox(BaseModel):
    x: float = Field(..., description="Relative X coordinate (0.0-1.0)")
    y: float = Field(..., description="Relative Y coordinate (0.0-1.0)")
    width: float = Field(..., description="Relative Width (0.0-1.0)")
    height: float = Field(..., description="Relative Height (0.0-1.0)")

class PageElement(BaseModel):
    type: str = Field(..., description="Element type: 'text', 'image', etc.")
    content: str = Field(..., description="Text content or image description")
    bbox: BoundingBox = Field(..., description="Bounding box of the element")

class SubChapter(BaseModel):
    subChapterId: str
    subChapterName: str
    isKeyPoint: bool
    pageRange: str
    elements: Optional[List[PageElement]] = Field(default=[], description="Page elements with coordinates")

class Chapter(BaseModel):
    chapterId: str
    chapterName: str
    subChapters: List[SubChapter]

class StructurePreview(BaseModel):
    chapters: List[Chapter]

class FileInfo(BaseModel):
    fileName: str
    fileSize: int
    pageCount: int

class ParseData(BaseModel):
    parseId: str
    fileInfo: FileInfo
    structurePreview: StructurePreview
    taskStatus: str = Field(..., description="processing, completed, failed")

class ParseResponse(BaseModel):
    code: int
    msg: str
    data: Optional[ParseData]
    requestId: str
