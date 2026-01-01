from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.core.base import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(Integer, unique=True, nullable=True)
    name = Column(String(50), nullable=True)
    surname = Column(String(50), nullable=True)
    birth_date = Column(Date, nullable=True)
    username = Column(String(100), unique=True, nullable=True)
    login = Column(String(100), unique=True, nullable=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=True)
    google_id = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    is_verified = Column(Boolean, nullable=False, default=False)
    terms_accepted = Column(Boolean, default=False, nullable=False)

    is_teacher = Column(Boolean, nullable=False, default=False)
    teacher = relationship("Teacher", back_populates="user", uselist=False, cascade="all, delete")
    avatar = relationship("UserAvatar", back_populates="user", uselist=False, cascade="all, delete")
    reviews = relationship("TeacherReview", back_populates="student", cascade="all, delete")
    enrollments = relationship("Enrollment", back_populates="user")


class PendingUser(Base):
    __tablename__ = "pending_users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=True)
    password_hash = Column(String, nullable=False)
    birth_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserAvatar(Base):
    __tablename__ = "user_avatars"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    file_path = Column(String, nullable=False)

    user = relationship("User", back_populates="avatar")