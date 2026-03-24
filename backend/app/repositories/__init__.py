"""
数据访问层 (Repository Pattern)
"""

try:
    from backend.app.repositories.qa_record_repository import QARecordRepository
    from backend.app.repositories.learning_progress_repository import LearningProgressRepository
except ImportError:
    from app.repositories.qa_record_repository import QARecordRepository
    from app.repositories.learning_progress_repository import LearningProgressRepository

__all__ = [
    "QARecordRepository",
    "LearningProgressRepository"
]
