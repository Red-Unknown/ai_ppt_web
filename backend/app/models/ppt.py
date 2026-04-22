"""
PPT/图片上传模型
对应 ppts 表
"""

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, func, JSON
from sqlalchemy.orm import relationship

try:
    from backend.app.core.database import Base
except ImportError:
    from app.core.database import Base


class PPT(Base):
    """PPT表"""
    __tablename__ = "ppts"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="PPT ID")
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, comment="所属课程ID")
    file_name = Column(String(255), nullable=False, comment="文件名")
    file_path = Column(String(500), comment="文件存储路径")
    file_size = Column(Integer, comment="文件大小(字节)")
    file_type = Column(String(50), comment="文件类型")
    slide_count = Column(Integer, default=0, comment="幻灯片数量")
    slides = Column(JSON, comment="幻灯片列表信息")
    parse_status = Column(String(20), default="pending", comment="解析状态: pending/parsing/completed/failed")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")

    # 关联关系
    course = relationship("NewCourse")

    def __repr__(self):
        return f"<PPT(id={self.id}, file_name={self.file_name})>"
