"""
课程 Repository
处理 courses、slides、course_documents 表的读写操作
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
import logging

try:
    from backend.app.models.course_new import NewCourse as Course, Slide, CourseDocument
    from backend.app.models.subject import Subject, Chapter
except ImportError:
    from app.models.course_new import NewCourse as Course, Slide, CourseDocument
    from app.models.subject import Subject, Chapter

logger = logging.getLogger(__name__)


class CourseRepository:
    """课程数据访问类"""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self, subject_id: int = None, chapter_id: int = None) -> List[Course]:
        """获取课程列表（可选过滤）"""
        try:
            query = self.db.query(Course)
            if subject_id:
                query = query.filter(Course.subject_id == subject_id)
            if chapter_id:
                query = query.filter(Course.chapter_id == chapter_id)
            return query.all()
        except Exception as e:
            logger.error(f"Failed to get courses: {e}")
            return []

    def get_by_id(self, course_id: int) -> Optional[Course]:
        """根据ID获取课程"""
        try:
            return self.db.query(Course).filter(Course.id == course_id).first()
        except Exception as e:
            logger.error(f"Failed to get course by id: {e}")
            return None

    def create(self, title: str, subject_id: int, chapter_id: int, description: str = None) -> Optional[Course]:
        """创建课程"""
        try:
            subject = self.db.query(Subject).filter(Subject.id == subject_id).first()
            if not subject:
                logger.warning(f"Subject not found: id={subject_id}")
                return None

            chapter = self.db.query(Chapter).filter(
                Chapter.id == chapter_id,
                Chapter.subject_id == subject_id
            ).first()
            if not chapter:
                logger.warning(f"Chapter not found: id={chapter_id}, subject_id={subject_id}")
                return None

            course = Course(
                title=title,
                subject_id=subject_id,
                chapter_id=chapter_id,
                description=description
            )
            self.db.add(course)
            self.db.commit()
            self.db.refresh(course)
            logger.info(f"Course created: id={course.id}, title={course.title}")
            return course
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create course: {e}")
            raise

    def update(self, course_id: int, title: str = None, description: str = None) -> Optional[Course]:
        """更新课程"""
        try:
            course = self.db.query(Course).filter(Course.id == course_id).first()
            if not course:
                return None
            if title is not None:
                course.title = title
            if description is not None:
                course.description = description
            self.db.commit()
            self.db.refresh(course)
            logger.info(f"Course updated: id={course_id}")
            return course
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update course: {e}")
            raise

    def delete(self, course_id: int) -> bool:
        """删除课程"""
        try:
            course = self.db.query(Course).filter(Course.id == course_id).first()
            if not course:
                return False
            self.db.delete(course)
            self.db.commit()
            logger.info(f"Course deleted: id={course_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete course: {e}")
            raise

    def get_slide_count(self, course_id: int) -> int:
        """获取课程幻灯片数量"""
        try:
            return self.db.query(Slide).filter(Slide.course_id == course_id).count()
        except Exception as e:
            logger.error(f"Failed to get slide count: {e}")
            return 0


class SlideRepository:
    """幻灯片数据访问类"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_course(self, course_id: int) -> List[Slide]:
        """获取课程的所有幻灯片"""
        try:
            return self.db.query(Slide).filter(
                Slide.course_id == course_id
            ).order_by(Slide.slide_index).all()
        except Exception as e:
            logger.error(f"Failed to get slides by course: {e}")
            return []

    def get_by_id(self, slide_id: int) -> Optional[Slide]:
        """根据ID获取幻灯片"""
        try:
            return self.db.query(Slide).filter(Slide.id == slide_id).first()
        except Exception as e:
            logger.error(f"Failed to get slide by id: {e}")
            return None

    def create(self, course_id: int, slide_index: int, **kwargs) -> Slide:
        """创建幻灯片"""
        try:
            slide = Slide(course_id=course_id, slide_index=slide_index, **kwargs)
            self.db.add(slide)
            self.db.commit()
            self.db.refresh(slide)
            logger.info(f"Slide created: id={slide.id}, course_id={course_id}")
            return slide
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create slide: {e}")
            raise

    def bulk_create(self, slides_data: List[Dict[str, Any]]) -> List[Slide]:
        """批量创建幻灯片"""
        try:
            slides = [Slide(**data) for data in slides_data]
            self.db.add_all(slides)
            self.db.commit()
            for slide in slides:
                self.db.refresh(slide)
            logger.info(f"Slides bulk created: count={len(slides)}")
            return slides
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to bulk create slides: {e}")
            raise

    def delete_by_course(self, course_id: int) -> int:
        """删除课程的所有幻灯片"""
        try:
            count = self.db.query(Slide).filter(Slide.course_id == course_id).delete()
            self.db.commit()
            logger.info(f"Slides deleted for course: course_id={course_id}, count={count}")
            return count
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete slides: {e}")
            raise


class CourseDocumentRepository:
    """课程文档数据访问类"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_course(self, course_id: int) -> List[CourseDocument]:
        """获取课程的所有文档"""
        try:
            return self.db.query(CourseDocument).filter(
                CourseDocument.course_id == course_id
            ).all()
        except Exception as e:
            logger.error(f"Failed to get documents by course: {e}")
            return []

    def get_by_id(self, document_id: int) -> Optional[CourseDocument]:
        """根据ID获取文档"""
        try:
            return self.db.query(CourseDocument).filter(
                CourseDocument.id == document_id
            ).first()
        except Exception as e:
            logger.error(f"Failed to get document by id: {e}")
            return None

    def create(self, course_id: int, title: str, content: str = None, doc_type: str = "text") -> CourseDocument:
        """创建文档"""
        try:
            document = CourseDocument(
                course_id=course_id,
                title=title,
                content=content,
                doc_type=doc_type
            )
            self.db.add(document)
            self.db.commit()
            self.db.refresh(document)
            logger.info(f"CourseDocument created: id={document.id}")
            return document
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create document: {e}")
            raise

    def delete(self, document_id: int) -> bool:
        """删除文档"""
        try:
            document = self.db.query(CourseDocument).filter(
                CourseDocument.id == document_id
            ).first()
            if not document:
                return False
            self.db.delete(document)
            self.db.commit()
            logger.info(f"CourseDocument deleted: id={document_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete document: {e}")
            raise
