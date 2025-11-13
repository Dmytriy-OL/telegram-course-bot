from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Date,Enum,Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.core.base import Base
from app.database.core.enums import LessonType
from datetime import datetime


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    type_lesson = Column(Enum(LessonType), nullable=False)  # Тип заняття (онлайн/офлайн)
    freely = Column(Boolean, default=True)
    places = Column(Integer, default=1)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), default=datetime.utcnow)

    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=True)
    teacher = relationship("Teacher", back_populates="lessons")

    # enrollments = relationship("Enrollment", back_populates="lesson")
    # course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    # course = relationship("Courses", back_populates="lessons")
    enrollments = relationship("Enrollment", back_populates="lesson", cascade="all, delete-orphan")


# class TutoringSession(Base):
#     __tablename__ = "tutoring_sessions"
#
#     id = Column(Integer, primary_key=True)
#     topic = Column(String(100), nullable=False)
#     datetime = Column(DateTime(timezone=True), nullable=False)
#     duration_minutes = Column(Integer, default=60)
#     status = Column(String(20), default="scheduled")

    # teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    # teacher = relationship("Teacher", back_populates="tutoring_sessions")
    #
    # student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # student = relationship("User")

    # created_at = Column(DateTime(timezone=True), server_default=func.now(), default=datetime.utcnow)


# class PrivateLesson(Base):
#     __tablename__ = "private_lessons"
#
#     id = Column(Integer, primary_key=True)
#     title = Column(String(100), nullable=False)
#     description = Column(String(300), nullable=True)
#
#     datetime = Column(DateTime(timezone=True), nullable=False)
#     duration_minutes = Column(Integer, default=60)
#
#     price = Column(Integer, nullable=True)
#
#     status = Column(String(20), default="scheduled")  # scheduled / completed / cancelled

    # teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    # teacher = relationship("Teacher", back_populates="private_lessons")
    #
    # student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # student = relationship("User")

    # created_at = Column(DateTime(timezone=True), server_default=func.now(), default=datetime.utcnow)


class Courses(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True)
    title = Column(String(50), unique=False, nullable=False)
    price = Column(Integer, unique=False, nullable=False)
    caption = Column(Text, nullable=False)
    lesson_count = Column(Integer, unique=False, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="SET NULL"))
    teacher = relationship("Teacher", back_populates="courses")

    avatar = relationship("CourseAvatar", back_populates="course", uselist=False, cascade="all, delete")

    modules = relationship("Module", back_populates="course", cascade="all, delete-orphan")


class CourseAvatar(Base):
    __tablename__ = "course_avatar"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), unique=True)
    file_name = Column(String, nullable=False)

    course = relationship("Courses", back_populates="avatar")


class Module(Base):
    __tablename__ = "modules"

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    notes = Column(Text, nullable=True)  # конспект уроку

    order = Column(Integer, nullable=False)  # порядок уроку в курсі (1,2,3…)

    is_active = Column(Boolean, default=False)  # чи урок відкритий для студента
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # зв’язок з курсом
    course_id = Column(Integer, ForeignKey("courses.id"))
    course = relationship("Courses", back_populates="modules")

    tasks = relationship("Task", back_populates="module", cascade="all, delete-orphan")

    videos = relationship("VideoModule", back_populates="module", cascade="all, delete-orphan")


class VideoModule(Base):
    __tablename__ = "video_modules"

    id = Column(Integer, primary_key=True)
    description = Column(String(250), nullable=False)
    video_url = Column(String(255), nullable=True)
    video_file = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    module_id = Column(Integer, ForeignKey("modules.id"))
    module = relationship("Module", back_populates="videos")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    question = Column(Text, nullable=False)
    filename_img = Column(String(50), unique=True, nullable=True)

    answers = relationship("Answer", back_populates="task", cascade="all, delete-orphan")

    module_id = Column(Integer, ForeignKey("modules.id"))
    module = relationship("Module", back_populates="tasks")


class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True)
    text = Column(String(255), nullable=False)
    is_correct = Column(Boolean, default=False)

    task_id = Column(Integer, ForeignKey("tasks.id"))
    task = relationship("Task", back_populates="answers")
