from .connection import db_manager
from .student_collection import student_collection
from .teacher_collection import teacher_collection
from .smtp_collection import smtp_config_collection, email_log_collection

__all__ = [
    "db_manager",
    "student_collection", 
    "teacher_collection",
    "smtp_config_collection",
    "email_log_collection"
]