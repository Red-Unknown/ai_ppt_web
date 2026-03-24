"""
学习进度模型
对应建表语句中的 learning_progress 表
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON, Text, Float, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

try:
    from backend.app.core.database import Base
except ImportError:
    from app.core.database import Base


class LearningProgress(Base):
    """学习进度与适配表"""
    __tablename__ = "learning_progress"

    track_id = Column(String(50), primary_key=True, comment="追踪ID")
    user_id = Column(String(50), ForeignKey("users.user_id"), comment="用户ID")
    session_id = Column(String(50), nullable=False, comment="会话ID，会话对齐")
    school_id = Column(String(50), nullable=False, comment="学校ID")
    lesson_id = Column(String(50), ForeignKey("lessons.lesson_id"), comment="课件ID")
    current_node_id = Column(String(50), ForeignKey("cir_sections.node_id"), comment="断点节点ID")
    current_path = Column(Text, comment="当前学习路径")
    current_topic = Column(Text, comment="当前主题")
    last_qa_query = Column(Text, comment="最近一次有效问答")
    confusion_count = Column(Integer, default=0, comment="困惑计数，触发退回/补讲")
    mastery = Column(JSON, default={}, comment="主题掌握度映射（如 {\"极限\": 0.73}）")
    last_position_seconds = Column(Integer, default=0, comment="最后位置（秒）")
    progress_percent = Column(Float, comment="进度百分比")
    adjust_type = Column(String(20), default="normal", comment="调整类型")
    needs_supplement = Column(Boolean, default=False, comment="是否需要补充学习")
    last_operate_time = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="最后操作时间")

    # 关系
    user = relationship("User")
    lesson = relationship("Lesson")
    current_node = relationship("CIRSection")

    def __repr__(self):
        return f"<LearningProgress(track_id={self.track_id}, user={self.user_id}, session={self.session_id})>"
