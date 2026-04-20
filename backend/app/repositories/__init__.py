"""
数据访问层 (Repository Pattern)
"""

try:
    from backend.app.repositories.qa_record_repository import QARecordRepository
    from backend.app.repositories.learning_progress_repository import LearningProgressRepository
    from backend.app.repositories.subject_repository import SubjectRepository, ChapterRepository
    from backend.app.repositories.course_repository import (
        CourseRepository, SlideRepository, CourseDocumentRepository
    )
    from backend.app.repositories.ppt_repository import PPTRepository
    from backend.app.repositories.script_repository import CIRSectionRepository
    from backend.app.repositories.lesson_repository import (
        CourseSystemRepository, LessonRepository, CourseCategoryRepository
    )
except ImportError:
    from app.repositories.qa_record_repository import QARecordRepository
    from app.repositories.learning_progress_repository import LearningProgressRepository
    from app.repositories.subject_repository import SubjectRepository, ChapterRepository
    from app.repositories.course_repository import (
        CourseRepository, SlideRepository, CourseDocumentRepository
    )
    from app.repositories.ppt_repository import PPTRepository
    from app.repositories.script_repository import CIRSectionRepository
    from app.repositories.lesson_repository import (
        CourseSystemRepository, LessonRepository, CourseCategoryRepository
    )

__all__ = [
    "QARecordRepository",
    "LearningProgressRepository",
    "SubjectRepository",
    "ChapterRepository",
    "CourseRepository",
    "SlideRepository",
    "CourseDocumentRepository",
    "PPTRepository",
    "CIRSectionRepository",
    "CourseSystemRepository",
    "LessonRepository",
    "CourseCategoryRepository"
]
