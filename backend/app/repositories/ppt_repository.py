"""
PPT Repository
处理 ppts 表的读写操作
"""

from typing import Optional, List
from sqlalchemy.orm import Session
import logging

try:
    from backend.app.models.ppt import PPT
except ImportError:
    from app.models.ppt import PPT

logger = logging.getLogger(__name__)


class PPTRepository:
    """PPT数据访问类"""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self, course_id: int = None) -> List[PPT]:
        """获取PPT列表（可选按课程过滤）"""
        try:
            query = self.db.query(PPT)
            if course_id:
                query = query.filter(PPT.course_id == course_id)
            return query.order_by(PPT.created_at.desc()).all()
        except Exception as e:
            logger.error(f"Failed to get PPTs: {e}")
            return []

    def get_by_id(self, ppt_id: int) -> Optional[PPT]:
        """根据ID获取PPT"""
        try:
            return self.db.query(PPT).filter(PPT.id == ppt_id).first()
        except Exception as e:
            logger.error(f"Failed to get PPT by id: {e}")
            return None

    def get_by_course(self, course_id: int) -> List[PPT]:
        """根据课程ID获取PPT列表"""
        try:
            return self.db.query(PPT).filter(
                PPT.course_id == course_id
            ).order_by(PPT.created_at.desc()).all()
        except Exception as e:
            logger.error(f"Failed to get PPTs by course: {e}")
            return []

    def create(
        self,
        course_id: int,
        file_name: str,
        file_path: str,
        file_size: int,
        file_type: str,
        parse_status: str = "pending"
    ) -> PPT:
        """创建PPT记录"""
        try:
            ppt = PPT(
                course_id=course_id,
                file_name=file_name,
                file_path=file_path,
                file_size=file_size,
                file_type=file_type,
                parse_status=parse_status
            )
            self.db.add(ppt)
            self.db.commit()
            self.db.refresh(ppt)
            logger.info(f"PPT created: id={ppt.id}, file_name={ppt.file_name}")
            return ppt
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create PPT: {e}")
            raise

    def update_parse_status(
        self,
        ppt_id: int,
        parse_status: str,
        slide_count: int = None,
        slides: dict = None
    ) -> Optional[PPT]:
        """更新PPT解析状态"""
        try:
            ppt = self.db.query(PPT).filter(PPT.id == ppt_id).first()
            if not ppt:
                return None
            ppt.parse_status = parse_status
            if slide_count is not None:
                ppt.slide_count = slide_count
            if slides is not None:
                ppt.slides = slides
            self.db.commit()
            self.db.refresh(ppt)
            logger.info(f"PPT parse status updated: id={ppt_id}, status={parse_status}")
            return ppt
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update PPT parse status: {e}")
            raise

    def delete(self, ppt_id: int) -> bool:
        """删除PPT记录"""
        try:
            ppt = self.db.query(PPT).filter(PPT.id == ppt_id).first()
            if not ppt:
                return False
            self.db.delete(ppt)
            self.db.commit()
            logger.info(f"PPT deleted: id={ppt_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete PPT: {e}")
            raise
