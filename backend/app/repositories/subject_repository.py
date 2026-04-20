"""
科目与章节 Repository
处理 subjects 和 chapters 表的读写操作
"""

from typing import Optional, List
from sqlalchemy.orm import Session
import logging

try:
    from backend.app.models.subject import Subject, Chapter
except ImportError:
    from app.models.subject import Subject, Chapter

logger = logging.getLogger(__name__)


class SubjectRepository:
    """科目数据访问类"""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Subject]:
        """获取所有科目"""
        try:
            return self.db.query(Subject).all()
        except Exception as e:
            logger.error(f"Failed to get subjects: {e}")
            return []

    def get_by_id(self, subject_id: int) -> Optional[Subject]:
        """根据ID获取科目"""
        try:
            return self.db.query(Subject).filter(Subject.id == subject_id).first()
        except Exception as e:
            logger.error(f"Failed to get subject by id: {e}")
            return None

    def create(self, name: str) -> Subject:
        """创建科目"""
        try:
            subject = Subject(name=name)
            self.db.add(subject)
            self.db.commit()
            self.db.refresh(subject)
            logger.info(f"Subject created: id={subject.id}, name={subject.name}")
            return subject
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create subject: {e}")
            raise

    def update(self, subject_id: int, name: str) -> Optional[Subject]:
        """更新科目"""
        try:
            subject = self.db.query(Subject).filter(Subject.id == subject_id).first()
            if not subject:
                return None
            subject.name = name
            self.db.commit()
            self.db.refresh(subject)
            logger.info(f"Subject updated: id={subject_id}")
            return subject
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update subject: {e}")
            raise

    def delete(self, subject_id: int) -> bool:
        """删除科目"""
        try:
            subject = self.db.query(Subject).filter(Subject.id == subject_id).first()
            if not subject:
                return False
            self.db.delete(subject)
            self.db.commit()
            logger.info(f"Subject deleted: id={subject_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete subject: {e}")
            raise


class ChapterRepository:
    """章节数据访问类"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_subject(self, subject_id: int) -> List[Chapter]:
        """根据科目ID获取章节列表"""
        try:
            return self.db.query(Chapter).filter(
                Chapter.subject_id == subject_id
            ).order_by(Chapter.order).all()
        except Exception as e:
            logger.error(f"Failed to get chapters by subject: {e}")
            return []

    def get_by_id(self, chapter_id: int) -> Optional[Chapter]:
        """根据ID获取章节"""
        try:
            return self.db.query(Chapter).filter(Chapter.id == chapter_id).first()
        except Exception as e:
            logger.error(f"Failed to get chapter by id: {e}")
            return None

    def create(self, subject_id: int, name: str, order: int = 0) -> Optional[Chapter]:
        """创建章节"""
        try:
            subject = self.db.query(Subject).filter(Subject.id == subject_id).first()
            if not subject:
                logger.warning(f"Subject not found: id={subject_id}")
                return None
            chapter = Chapter(subject_id=subject_id, name=name, order=order)
            self.db.add(chapter)
            self.db.commit()
            self.db.refresh(chapter)
            logger.info(f"Chapter created: id={chapter.id}, name={chapter.name}")
            return chapter
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create chapter: {e}")
            raise

    def update(self, chapter_id: int, name: str = None, order: int = None) -> Optional[Chapter]:
        """更新章节"""
        try:
            chapter = self.db.query(Chapter).filter(Chapter.id == chapter_id).first()
            if not chapter:
                return None
            if name is not None:
                chapter.name = name
            if order is not None:
                chapter.order = order
            self.db.commit()
            self.db.refresh(chapter)
            logger.info(f"Chapter updated: id={chapter_id}")
            return chapter
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update chapter: {e}")
            raise

    def delete(self, chapter_id: int) -> bool:
        """删除章节"""
        try:
            chapter = self.db.query(Chapter).filter(Chapter.id == chapter_id).first()
            if not chapter:
                return False
            self.db.delete(chapter)
            self.db.commit()
            logger.info(f"Chapter deleted: id={chapter_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete chapter: {e}")
            raise
