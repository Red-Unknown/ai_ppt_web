"""
学习进度 Repository
处理 learning_progress 表的读写操作
"""

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
import logging
import uuid

try:
    from backend.app.models.progress import LearningProgress
except ImportError:
    from app.models.progress import LearningProgress

logger = logging.getLogger(__name__)


class LearningProgressRepository:
    """学习进度数据访问类"""

    def __init__(self, db: Session):
        self.db = db

    def upsert_progress(
        self,
        user_id: str,
        session_id: str,
        school_id: str,
        lesson_id: Optional[str] = None,
        current_node_id: Optional[str] = None,
        current_path: Optional[str] = None,
        current_topic: Optional[str] = None,
        last_qa_query: Optional[str] = None,
        confusion_count: Optional[int] = None,
        mastery: Optional[Dict[str, float]] = None,
        last_position_seconds: Optional[int] = None,
        progress_percent: Optional[float] = None,
        adjust_type: Optional[str] = None,
        needs_supplement: Optional[bool] = None
    ) -> LearningProgress:
        """
        更新或创建学习进度记录

        Args:
            user_id: 用户ID
            session_id: 会话ID
            school_id: 学校ID
            lesson_id: 课件ID
            current_node_id: 当前节点ID
            current_path: 当前学习路径
            current_topic: 当前主题
            last_qa_query: 最近一次问答
            confusion_count: 困惑计数
            mastery: 掌握度映射
            last_position_seconds: 最后位置（秒）
            progress_percent: 进度百分比
            adjust_type: 调整类型
            needs_supplement: 是否需要补充

        Returns:
            LearningProgress: 更新后的学习进度记录
        """
        try:
            # 生成 track_id（基于 user_id + session_id）
            track_id = f"{user_id}_{session_id}"

            # 检查记录是否存在
            existing = self.db.query(LearningProgress).filter(
                LearningProgress.track_id == track_id
            ).first()

            if existing:
                # 更新现有记录
                if lesson_id is not None:
                    existing.lesson_id = lesson_id
                if current_node_id is not None:
                    existing.current_node_id = current_node_id
                if current_path is not None:
                    existing.current_path = current_path
                if current_topic is not None:
                    existing.current_topic = current_topic
                if last_qa_query is not None:
                    existing.last_qa_query = last_qa_query
                if confusion_count is not None:
                    existing.confusion_count = confusion_count
                if mastery is not None:
                    existing.mastery = mastery
                if last_position_seconds is not None:
                    existing.last_position_seconds = last_position_seconds
                if progress_percent is not None:
                    existing.progress_percent = progress_percent
                if adjust_type is not None:
                    existing.adjust_type = adjust_type
                if needs_supplement is not None:
                    existing.needs_supplement = needs_supplement

                self.db.commit()
                self.db.refresh(existing)

                logger.info(f"Learning progress updated: track_id={track_id}")
                return existing
            else:
                # 创建新记录
                progress = LearningProgress(
                    track_id=track_id,
                    user_id=user_id,
                    session_id=session_id,
                    school_id=school_id,
                    lesson_id=lesson_id,
                    current_node_id=current_node_id,
                    current_path=current_path,
                    current_topic=current_topic,
                    last_qa_query=last_qa_query,
                    confusion_count=confusion_count or 0,
                    mastery=mastery or {},
                    last_position_seconds=last_position_seconds or 0,
                    progress_percent=progress_percent,
                    adjust_type=adjust_type or "normal",
                    needs_supplement=needs_supplement or False
                )

                self.db.add(progress)
                self.db.commit()
                self.db.refresh(progress)

                logger.info(f"Learning progress created: track_id={track_id}")
                return progress

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to upsert learning progress: {e}")
            raise

    def get_progress_by_session(
        self,
        user_id: str,
        session_id: str
    ) -> Optional[LearningProgress]:
        """
        获取会话的学习进度

        Args:
            user_id: 用户ID
            session_id: 会话ID

        Returns:
            Optional[LearningProgress]: 学习进度记录，如果没有则返回 None
        """
        try:
            track_id = f"{user_id}_{session_id}"

            progress = self.db.query(LearningProgress).filter(
                LearningProgress.track_id == track_id
            ).first()

            return progress

        except Exception as e:
            logger.error(f"Failed to get learning progress: {e}")
            return None

    def get_progress_by_user(
        self,
        user_id: str,
        limit: int = 10
    ) -> list:
        """
        获取用户的学习进度列表

        Args:
            user_id: 用户ID
            limit: 返回记录数量限制

        Returns:
            list: 学习进度记录列表
        """
        try:
            progresses = self.db.query(LearningProgress).filter(
                LearningProgress.user_id == user_id
            ).order_by(
                LearningProgress.last_operate_time.desc()
            ).limit(limit).all()

            return progresses

        except Exception as e:
            logger.error(f"Failed to get learning progresses by user: {e}")
            return []

    def increment_confusion(
        self,
        user_id: str,
        session_id: str
    ) -> Optional[LearningProgress]:
        """
        增加困惑计数

        Args:
            user_id: 用户ID
            session_id: 会话ID

        Returns:
            Optional[LearningProgress]: 更新后的学习进度记录
        """
        try:
            track_id = f"{user_id}_{session_id}"

            progress = self.db.query(LearningProgress).filter(
                LearningProgress.track_id == track_id
            ).first()

            if progress:
                progress.confusion_count += 1
                self.db.commit()
                self.db.refresh(progress)

                logger.info(f"Confusion count incremented: track_id={track_id}, count={progress.confusion_count}")
                return progress
            else:
                logger.warning(f"Learning progress not found for confusion increment: track_id={track_id}")
                return None

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to increment confusion count: {e}")
            return None

    def reset_confusion(
        self,
        user_id: str,
        session_id: str
    ) -> Optional[LearningProgress]:
        """
        重置困惑计数

        Args:
            user_id: 用户ID
            session_id: 会话ID

        Returns:
            Optional[LearningProgress]: 更新后的学习进度记录
        """
        try:
            track_id = f"{user_id}_{session_id}"

            progress = self.db.query(LearningProgress).filter(
                LearningProgress.track_id == track_id
            ).first()

            if progress:
                progress.confusion_count = 0
                self.db.commit()
                self.db.refresh(progress)

                logger.info(f"Confusion count reset: track_id={track_id}")
                return progress
            else:
                logger.warning(f"Learning progress not found for confusion reset: track_id={track_id}")
                return None

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to reset confusion count: {e}")
            return None

    def update_mastery(
        self,
        user_id: str,
        session_id: str,
        topic: str,
        score: float
    ) -> Optional[LearningProgress]:
        """
        更新主题掌握度

        Args:
            user_id: 用户ID
            session_id: 会话ID
            topic: 主题名称
            score: 掌握度分数（0-1）

        Returns:
            Optional[LearningProgress]: 更新后的学习进度记录
        """
        try:
            track_id = f"{user_id}_{session_id}"

            progress = self.db.query(LearningProgress).filter(
                LearningProgress.track_id == track_id
            ).first()

            if progress:
                if progress.mastery is None:
                    progress.mastery = {}

                progress.mastery[topic] = score
                self.db.commit()
                self.db.refresh(progress)

                logger.info(f"Mastery updated: track_id={track_id}, topic={topic}, score={score}")
                return progress
            else:
                logger.warning(f"Learning progress not found for mastery update: track_id={track_id}")
                return None

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update mastery: {e}")
            return None
