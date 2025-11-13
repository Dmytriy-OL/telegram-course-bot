from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Date,Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.core.base import Base
from app.database.core.enums import LessonType
from datetime import datetime


class Administrator(Base):
    __tablename__ = "administrators"

    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, unique=True, nullable=True)
    name = Column(String(50), unique=False, nullable=False)
    surname = Column(String(50), unique=False, nullable=False)
    login = Column(String(100), unique=True, nullable=True)
    main_admin = Column(Boolean, default=False)