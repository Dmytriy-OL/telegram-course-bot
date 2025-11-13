from enum import Enum


class LessonType(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"


class EnglishLevel(str, Enum):
    B2 = "Upper Intermediate (B2)"
    C1 = "Advanced (C1)"
    C2 = "Proficiency (C2)"
    NATIVE = "Native Speaker"


class GenderSelection(str, Enum):
    MEN = "Men"
    WOMEN = "Women"
