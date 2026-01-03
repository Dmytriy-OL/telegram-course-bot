from pydantic import BaseModel


class TeacherApplicationCreate(BaseModel):
    name: str
    surname: str
    language: str
    experience: str
    english_level: str
    price: float
    phone: str
    bio: str
    social_networks: dict[str, str]
