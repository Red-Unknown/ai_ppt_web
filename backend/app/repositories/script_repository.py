"""
CIR (Course Intermediate Representation) Section Repository
处理 cir_sections 表的读写操作
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
import logging

try:
    from backend.app.models.cir import CIRSection
except ImportError:
    from app.models.cir import CIRSection

logger = logging.getLogger(__name__)


class CIRSectionRepository:
    """CIR节点数据访问类"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_lesson(self, lesson_id: str) -> List[CIRSection]:
        """根据课件ID获取所有节点（按排序）"""
        try:
            return self.db.query(CIRSection).filter(
                CIRSection.lesson_id == lesson_id
            ).order_by(CIRSection.sort_order).all()
        except Exception as e:
            logger.error(f"Failed to get CIR sections by lesson: {e}")
            return []

    def get_by_id(self, node_id: str) -> Optional[CIRSection]:
        """根据节点ID获取节点"""
        try:
            return self.db.query(CIRSection).filter(
                CIRSection.node_id == node_id
            ).first()
        except Exception as e:
            logger.error(f"Failed to get CIR section by id: {e}")
            return None

    def get_by_course(self, course_id: str) -> List[CIRSection]:
        """根据课程ID获取所有节点"""
        try:
            return self.db.query(CIRSection).filter(
                CIRSection.lesson_id.like(f"{course_id}%")
            ).all()
        except Exception as e:
            logger.error(f"Failed to get CIR sections by course: {e}")
            return []

    def create(self, **kwargs) -> CIRSection:
        """创建CIR节点"""
        try:
            section = CIRSection(**kwargs)
            self.db.add(section)
            self.db.commit()
            self.db.refresh(section)
            logger.info(f"CIR section created: node_id={section.node_id}")
            return section
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create CIR section: {e}")
            raise

    def bulk_create(self, sections_data: List[Dict[str, Any]]) -> List[CIRSection]:
        """批量创建CIR节点"""
        try:
            sections = [CIRSection(**data) for data in sections_data]
            self.db.add_all(sections)
            self.db.commit()
            for section in sections:
                self.db.refresh(section)
            logger.info(f"CIR sections bulk created: count={len(sections)}")
            return sections
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to bulk create CIR sections: {e}")
            raise

    def update_script(self, node_id: str, script_content: str) -> Optional[CIRSection]:
        """更新节点讲稿内容"""
        try:
            section = self.db.query(CIRSection).filter(
                CIRSection.node_id == node_id
            ).first()
            if not section:
                return None
            section.script_content = script_content
            self.db.commit()
            self.db.refresh(section)
            logger.info(f"CIR section script updated: node_id={node_id}")
            return section
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update CIR section script: {e}")
            raise

    def reset_script(self, node_id: str) -> bool:
        """重置节点讲稿内容"""
        try:
            section = self.db.query(CIRSection).filter(
                CIRSection.node_id == node_id
            ).first()
            if not section:
                return False
            section.script_content = None
            self.db.commit()
            logger.info(f"CIR section script reset: node_id={node_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to reset CIR section script: {e}")
            raise

    def bulk_update_scripts(self, scripts: Dict[str, str]) -> List[str]:
        """批量更新多个节点的讲稿内容"""
        try:
            updated = []
            for node_id, script_content in scripts.items():
                section = self.db.query(CIRSection).filter(
                    CIRSection.node_id == node_id
                ).first()
                if section:
                    section.script_content = script_content
                    updated.append(node_id)
            self.db.commit()
            logger.info(f"CIR section scripts bulk updated: count={len(updated)}")
            return updated
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to bulk update CIR section scripts: {e}")
            raise

    def delete_by_lesson(self, lesson_id: str) -> int:
        """删除课件的所有节点"""
        try:
            count = self.db.query(CIRSection).filter(
                CIRSection.lesson_id == lesson_id
            ).delete()
            self.db.commit()
            logger.info(f"CIR sections deleted for lesson: lesson_id={lesson_id}, count={count}")
            return count
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete CIR sections: {e}")
            raise

    def delete(self, node_id: str) -> bool:
        """删除单个节点"""
        try:
            section = self.db.query(CIRSection).filter(
                CIRSection.node_id == node_id
            ).first()
            if not section:
                return False
            self.db.delete(section)
            self.db.commit()
            logger.info(f"CIR section deleted: node_id={node_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete CIR section: {e}")
            raise
