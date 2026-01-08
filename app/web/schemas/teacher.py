from pydantic import BaseModel
from app.database.core.enums import EnglishLevel


class TeacherLanguageCreate(BaseModel):
    language: str
    level: EnglishLevel
    price: float


class TeacherApplicationCreate(BaseModel):
    name: str
    surname: str
    experience: str
    phone: str
    bio: str
    social_networks: dict[str, str]
    languages: list[TeacherLanguageCreate]


class ProfileUpdateData(BaseModel):
    first_name: str
    last_name: str

