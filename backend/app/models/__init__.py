"""
ORM Models for PostgreSQL
"""

from backend.app.models.user import User
from backend.app.models.course import Course, CourseCategory, Lesson
from backend.app.models.course_new import NewCourse, Slide, CourseDocument, LessonPlan
from backend.app.models.cir import CIRSection
from backend.app.models.qa import QARecord
from backend.app.models.progress import LearningProgress
from backend.app.models.subject import Subject, Chapter
from backend.app.models.ppt import PPT

__all__ = [
    "User",
    "Course",
    "CourseCategory",
    "Lesson",
    "NewCourse",
    "Slide",
    "CourseDocument",
    "LessonPlan",
    "CIRSection",
    "QARecord",
    "LearningProgress",
    "Subject",
    "Chapter",
    "PPT"
]
