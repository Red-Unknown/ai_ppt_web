"""
问答记录模型
对应建表语句中的 qa_records 表
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON, Text, Float, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

try:
    from backend.app.core.database import Base
except ImportError:
    from app.core.database import Base


class QARecord(Base):
    """问答记录表"""
    __tablename__ = "qa_records"

    answer_id = Column(Integer, primary_key=True, autoincrement=True, comment="回答ID")
    session_id = Column(String(50), nullable=False, comment="会话ID，相同会话代表多轮追问")
    user_id = Column(String(50), ForeignKey("users.user_id"), comment="用户ID")
    school_id = Column(String(50), nullable=False, comment="学校ID")
    lesson_id = Column(String(50), ForeignKey("lessons.lesson_id"), comment="课件ID（允许为空）")
    question_type = Column(String(10), comment="问题类型")
    question_text = Column(Text, nullable=False, comment="问题内容")
    answer_text = Column(Text, nullable=False, comment="回答内容")
    cited_node_id = Column(String(50), ForeignKey("cir_sections.node_id"), comment="主引用节点ID")
    source_page_num = Column(Integer, comment="主引用页码")
    sources = Column(JSON, comment="多来源证据数组，包含bbox, score等前端高亮信息")
    current_path = Column(Text, comment="提问时的学习路径")
    video_timestamp = Column(Float, comment="播放器时间戳（秒），用于精准续接")
    understanding_level = Column(String(20), comment="理解程度")
    response_ms = Column(Integer, comment="响应时间（毫秒）")
    is_accurate = Column(Boolean, comment="是否准确")
    reasoning_content = Column(Text, comment="reasoner的思考过程")
    tool_calls = Column(JSON, comment="工具调用记录（web_search等）")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")

    # 关系
    user = relationship("User")
    lesson = relationship("Lesson")
    cited_node = relationship("CIRSection")

    def __repr__(self):
        return f"<QARecord(id={self.answer_id}, session={self.session_id}, user={self.user_id})>"
