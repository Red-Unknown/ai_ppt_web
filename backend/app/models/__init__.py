"""
ORM Models for PostgreSQL
"""

try:
    from backend.app.models.user import User
    from backend.app.models.course import CourseCategory, Course, Lesson
    from backend.app.models.cir import CIRSection
    from backend.app.models.qa import QARecord
    from backend.app.models.progress import LearningProgress
except ImportError:
    from app.models.user import User
    from app.models.course import CourseCategory, Course, Lesson
    from app.models.cir import CIRSection
    from app.models.qa import QARecord
    from app.models.progress import LearningProgress

__all__ = [
    "User",
    "CourseCategory",
    "Course",
    "Lesson",
    "CIRSection",
    "QARecord",
    "LearningProgress"
]
