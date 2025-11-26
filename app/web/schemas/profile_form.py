from pydantic import BaseModel, computed_field
from datetime import date


class ProfileUpdateForm(BaseModel):
    name: str
    surname: str
    username: str | None = None
    birth_day: int
    birth_month: int
    birth_year: int

    @computed_field
    @property
    def birth_date(self) -> date:
        try:
            return date(self.birth_year, self.birth_month, self.birth_day)
        except ValueError:
            raise ValueError("Невірна дата народження")
