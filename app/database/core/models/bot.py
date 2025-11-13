from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Date,Enum,JSON,Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.core.base import Base
from app.database.core.enums import LessonType,GenderSelection,EnglishLevel
from datetime import datetime


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