"""
问答记录 Repository
处理 qa_records 表的读写操作
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
import logging
import time

try:
    from backend.app.models.qa import QARecord
except ImportError:
    from app.models.qa import QARecord

logger = logging.getLogger(__name__)


class QARecordRepository:
    """问答记录数据访问类"""

    def __init__(self, db: Session):
        self.db = db

    def create_record(
        self,
        session_id: str,
        user_id: str,
        school_id: str,
        question_text: str,
        answer_text: str,
        question_type: Optional[str] = None,
        lesson_id: Optional[str] = None,
        cited_node_id: Optional[str] = None,
        source_page_num: Optional[int] = None,
        sources: Optional[List[Dict[str, Any]]] = None,
        current_path: Optional[str] = None,
        video_timestamp: Optional[float] = None,
        understanding_level: Optional[str] = None,
        response_ms: Optional[int] = None,
        is_accurate: Optional[bool] = None,
        reasoning_content: Optional[str] = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None
    ) -> QARecord:
        """
        创建问答记录

        Args:
            session_id: 会话ID
            user_id: 用户ID
            school_id: 学校ID
            question_text: 问题内容
            answer_text: 回答内容
            question_type: 问题类型
            lesson_id: 课件ID
            cited_node_id: 引用的节点ID
            source_page_num: 引用页码
            sources: 证据来源数组
            current_path: 当前学习路径
            video_timestamp: 视频时间戳
            understanding_level: 理解程度
            response_ms: 响应时间（毫秒）
            is_accurate: 是否准确
            reasoning_content: 推理过程
            tool_calls: 工具调用记录

        Returns:
            QARecord: 创建的问答记录
        """
        try:
            record = QARecord(
                session_id=session_id,
                user_id=user_id,
                school_id=school_id,
                question_text=question_text,
                answer_text=answer_text,
                question_type=question_type,
                lesson_id=lesson_id,
                cited_node_id=cited_node_id,
                source_page_num=source_page_num,
                sources=sources,
                current_path=current_path,
                video_timestamp=video_timestamp,
                understanding_level=understanding_level,
                response_ms=response_ms,
                is_accurate=is_accurate,
                reasoning_content=reasoning_content,
                tool_calls=tool_calls
            )

            self.db.add(record)
            self.db.commit()
            self.db.refresh(record)

            logger.info(f"QA record created: answer_id={record.answer_id}, session={session_id}")
            return record

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create QA record: {e}")
            raise

    def get_records_by_session(
        self,
        session_id: str,
        limit: int = 50
    ) -> List[QARecord]:
        """
        获取会话的问答记录

        Args:
            session_id: 会话ID
            limit: 返回记录数量限制

        Returns:
            List[QARecord]: 问答记录列表
        """
        try:
            records = self.db.query(QARecord).filter(
                QARecord.session_id == session_id
            ).order_by(
                desc(QARecord.created_at)
            ).limit(limit).all()

            return records

        except Exception as e:
            logger.error(f"Failed to get QA records by session: {e}")
            return []

    def get_records_by_user(
        self,
        user_id: str,
        limit: int = 100
    ) -> List[QARecord]:
        """
        获取用户的问答记录

        Args:
            user_id: 用户ID
            limit: 返回记录数量限制

        Returns:
            List[QARecord]: 问答记录列表
        """
        try:
            records = self.db.query(QARecord).filter(
                QARecord.user_id == user_id
            ).order_by(
                desc(QARecord.created_at)
            ).limit(limit).all()

            return records

        except Exception as e:
            logger.error(f"Failed to get QA records by user: {e}")
            return []

    def get_latest_record_by_session(
        self,
        session_id: str
    ) -> Optional[QARecord]:
        """
        获取会话最新的问答记录

        Args:
            session_id: 会话ID

        Returns:
            Optional[QARecord]: 最新的问答记录，如果没有则返回 None
        """
        try:
            record = self.db.query(QARecord).filter(
                QARecord.session_id == session_id
            ).order_by(
                desc(QARecord.created_at)
            ).first()

            return record

        except Exception as e:
            logger.error(f"Failed to get latest QA record: {e}")
            return None
