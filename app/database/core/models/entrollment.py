from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Date,Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.core.base import Base
from app.database.core.enums import LessonType
from datetime import datetime


class Enrollment(Base):
    """Таблиця, яка зберігає записи користувачів на заняття"""
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True)
    user_tg_id = Column(Integer, ForeignKey("users.tg_id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    full_name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), default=datetime.utcnow)

    user = relationship("User", back_populates="enrollments")
    lesson = relationship("Lesson", back_populates="enrollments")