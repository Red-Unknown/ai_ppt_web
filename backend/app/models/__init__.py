"""
ORM Models for PostgreSQL
"""

try:
    from backend.app.models.user import User
    from backend.app.models.course import CourseCategory, Course, Lesson
    from backend.app.models.cir import CIRSection
    from backend.app.models.qa import QARecord
    from backend.app.models.progress import LearningProgress
    from backend.app.models.subject import Subject, Chapter
    from backend.app.models.course_new import NewCourse, Slide, CourseDocument, LessonPlan
    from backend.app.models.ppt import PPT
except ImportError:
    from app.models.user import User
    from app.models.course import CourseCategory, Course, Lesson
    from app.models.cir import CIRSection
    from app.models.qa import QARecord
    from app.models.progress import LearningProgress
    from app.models.subject import Subject, Chapter
    from app.models.course_new import NewCourse, Slide, CourseDocument, LessonPlan
    from app.models.ppt import PPT

__all__ = [
    "User",
    "CourseCategory",
    "Course",
    "Lesson",
    "CIRSection",
    "QARecord",
    "LearningProgress",
    "Subject",
    "Chapter",
    "NewCourse",
    "Slide",
    "CourseDocument",
    "LessonPlan",
    "PPT"
]
