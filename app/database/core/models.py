from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import sessionmaker, DeclarativeBase, relationship, declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, LargeBinary, Text, Enum
from datetime import datetime
from dotenv import load_dotenv
from app.database.core.config import SQLALCHEMY_URL
from enum import Enum as PyEnum
import os

load_dotenv()

engine = create_async_engine(SQLALCHEMY_URL)

SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class LessonType(PyEnum):
    ONLINE = "online"
    OFFLINE = "offline"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(Integer, unique=True, nullable=True)
    name = Column(String(50), unique=False, nullable=True)
    surname = Column(String(50), unique=False, nullable=True)
    login = Column(String(100), unique=True, nullable=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=True, unique=False)
    google_id = Column(String, unique=True, nullable=True)

    enrollments = relationship("Enrollment", back_populates="user")


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    datetime = Column(DateTime, nullable=False, default=datetime.utcnow)  # Дата і час заняття
    type_lesson = Column(Enum(LessonType), nullable=False)  # Тип заняття (онлайн/офлайн)
    freely = Column(Boolean, default=True)
    places = Column(Integer, default=1)

    teacher_id = Column(Integer, ForeignKey("administrators.id"), nullable=False)

    enrollments = relationship("Enrollment", back_populates="lesson")
    administrator = relationship("Administrator", back_populates="lessons")


class Enrollment(Base):
    """Таблиця, яка зберігає записи користувачів на заняття"""
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True)
    user_tg_id = Column(Integer, ForeignKey("users.tg_id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    full_name = Column(String(100), nullable=False)
    user = relationship("User", back_populates="enrollments")
    lesson = relationship("Lesson", back_populates="enrollments")


class Administrator(Base):
    __tablename__ = "administrators"

    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, unique=True, nullable=False)
    name = Column(String(50), unique=False, nullable=False)
    surname = Column(String(50), unique=False, nullable=False)
    login = Column(String(100), unique=True, nullable=False)
    main_admin = Column(Boolean, default=False)

    lessons = relationship("Lesson", back_populates="administrator")


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True)
    filename = Column(String(50), unique=True, nullable=False)
    main_image = Column(Boolean, default=False)


class Caption(Base):
    __tablename__ = "caption"

    id = Column(Integer, primary_key=True)
    title = Column(String(50), unique=True, nullable=False)
    caption = Column(Text, nullable=False)
    main = Column(Boolean, default=False)
