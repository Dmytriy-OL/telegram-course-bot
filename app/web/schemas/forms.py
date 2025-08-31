from pydantic import BaseModel, EmailStr, field_validator, ValidationInfo
from datetime import date
from pydantic import computed_field


class RegisterForm(BaseModel):
    birth_day: int
    birth_month: int
    birth_year: int
    email: str
    username: str
    password: str
    password_confirm: str
    terms: bool

    @field_validator("password_confirm")
    @classmethod
    def passwords_match(cls, v, info):
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Паролі не співпадають")
        return v

    @computed_field
    @property
    def birth_date(self) -> date:
        try:
            return date(self.birth_year, self.birth_month, self.birth_day)
        except ValueError as e:
            raise ValueError(f"Невірна дата народження!!!")

    @field_validator("terms")
    @classmethod
    def terms_must_be_true(cls, v):
        if v is not True:
            raise ValueError("Ви маєте прийняти умови політики")
        return v


class PasswordForm(BaseModel):
    token: str
    password: str
    password_confirm: str

    @field_validator("password_confirm")
    @classmethod
    def passwords_match(cls, v, info):
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Паролі не співпадають")
        return v
