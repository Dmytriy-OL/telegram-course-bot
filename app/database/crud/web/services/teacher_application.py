from fastapi import UploadFile

from app.database.crud.web.teacher.exceptions import UserAlreadyTeacherError
from app.database.crud.web.user.repository import UserRepository
from app.web.schemas.teacher import TeacherApplicationCreate, ProfileUpdateData
from app.database.core.models import User, UserAvatar
from app.database.crud.web.teacher.repository import TeacherRepository
from app.web.utils.image_handler import save_avatar_to_disk


class TeacherApplicationService:

    def __init__(self, repo: TeacherRepository):
        self.repo = repo

    async def apply(self, user: User, data: TeacherApplicationCreate):
        # 🔐 бізнес-перевірки
        if user.is_teacher:
            raise UserAlreadyTeacherError("Ви вже маєте статус викладача")

        if not data.languages:
            raise ValueError("Потрібно додати хоча б одну мову")

        # 🧠 тут можуть бути:
        # - moderation
        # - логування
        # - нотифікації

        return await self.repo.create_teacher(user, data)


class ProfileService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def update_profile(
        self,
        user: User,
        data: ProfileUpdateData,
        avatar: UploadFile | None
    ):
        if avatar:
            file_name = await save_avatar_to_disk(avatar)

            if user.avatar:
                user.avatar.file_path = file_name
            else:
                user.avatar = UserAvatar(file_path=file_name)

        await self.repo.update_user(user, data)

