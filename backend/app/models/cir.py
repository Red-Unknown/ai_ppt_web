"""
CIR (Course Intermediate Representation) 模型
对应建表语句中的 cir_sections 表
"""

from sqlalchemy import Column, String, Integer, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship

try:
    from backend.app.core.database import Base
except ImportError:
    from app.core.database import Base


class CIRSection(Base):
    """CIR 课程中间结构表"""
    __tablename__ = "cir_sections"

    node_id = Column(String(50), primary_key=True, comment="节点ID")
    lesson_id = Column(String(50), ForeignKey("lessons.lesson_id"), comment="课件ID")
    school_id = Column(String(50), nullable=False, comment="学校ID")
    node_name = Column(String(200), nullable=False, comment="节点标题")
    parent_id = Column(String(50), ForeignKey("cir_sections.node_id"), comment="父节点ID")
    node_type = Column(String(20), comment="节点类型：chapter/subchapter/point")
    sort_order = Column(Integer, default=0, comment="排序")
    path = Column(Text, comment="节点路径（如 /chapter1/section2/point3）")
    page_num = Column(Integer, comment="对应PPT页码")
    image_url = Column(String(500), comment="页面图片")
    bbox = Column(JSON, comment="答案高亮定位框 [x, y, w, h]")
    key_points = Column(JSON, comment="知识点")
    teaching_content = Column(Text, comment="教学内容")
    script_content = Column(Text, comment="讲稿内容")
    duration_seconds = Column(Integer, comment="时长（秒）")
    audio_url = Column(String(500), comment="音频URL")
    media_resources = Column(JSON, comment="媒体资源")
    is_teacher_edited = Column(Boolean, default=False, comment="是否教师编辑过")

    # 关系
    lesson = relationship("Lesson", back_populates="cir_sections")
    parent = relationship("CIRSection", remote_side=[node_id], backref="children")

    def __repr__(self):
        return f"<CIRSection(id={self.node_id}, name={self.node_name}, type={self.node_type})>"
