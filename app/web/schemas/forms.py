from pydantic import BaseModel, EmailStr, field_validator, ValidationInfo


class RegisterForm(BaseModel):
    email: str
    password: str
    password_confirm: str

    @field_validator("password_confirm")
    @classmethod
    def passwords_match(cls, v, info):
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Паролі не співпадають")
        return v
