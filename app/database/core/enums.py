from enum import Enum


class LessonType(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"


class EnglishLevel(str, Enum):
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"
    Native = "Native"


class GenderSelection(str, Enum):
    MEN = "Men"
    WOMEN = "Women"
