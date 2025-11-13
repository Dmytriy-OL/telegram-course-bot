from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Date,Enum,Float,JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.core.base import Base
from app.database.core.enums import LessonType,GenderSelection,EnglishLevel
from datetime import datetime


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    surname = Column(String(50), nullable=False)
    photo = Column(String(255), nullable=True)  # шлях до фото
    sex = Column(Enum(GenderSelection), nullable=False)
    students_count = Column(Integer, default=0)  # вчив студентів
    experience_years = Column(Integer, default=0)  # років досвід

    roles = Column(JSON, default=lambda: [
        "General English Tutor",
        "Grammar Coach",
        "Vocabulary Trainer",
        "Speaking Coach",
        "Pronunciation Specialist",
        "Listening Skills Mentor",
        "Reading & Writing Instructor",
        "Exam Prep Expert (IELTS/TOEFL/Cambridge)",
        "Business English Trainer",
        "Corporate English Coach",
        "Kids English Teacher",
        "Academic English Teacher",
        "Travel English Instructor",
        "Immigration English Mentor",
        "Conversation Club Host",
        "Course Author",
        "Mentor & Progress Supervisor",
        "Interview & Job Prep Coach",
        "TOEIC Specialist",
        "Accent Reduction Coach",
        "Phonetics Trainer"
    ])
    english_level = Column(Enum(EnglishLevel), nullable=False,default=EnglishLevel.B2)
    description = Column(String(500), nullable=True)
    phone_number=Column(Integer,nullable=False)
    show_phone = Column(Boolean, default=False)
    social_links = Column(JSON, default=lambda: {
        "facebook": None,
        "instagram": None,
        "telegram": None,
        "youtube": None
    })
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    reviews = relationship("TeacherReview", back_populates="teacher", cascade="all, delete")
    lessons = relationship("Lesson", back_populates="teacher")
    courses = relationship("Courses", back_populates="teacher")


class TeacherReview(Base):
    __tablename__ = "teacher_reviews"

    id = Column(Integer, primary_key=True)

    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="CASCADE"))
    student_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    rating = Column(Float, nullable=False)  # ⭐ від 1 до 5
    review_text = Column(String(500), nullable=True)  # текст відгуку
    created_at = Column(DateTime, default=datetime.utcnow)

    teacher = relationship("Teacher", back_populates="reviews")
    student = relationship("User", back_populates="reviews")