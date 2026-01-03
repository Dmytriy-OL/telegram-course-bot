from app.web.schemas.teacher import TeacherApplicationCreate
from app.database.core.models import User
from app.database.crud.web.teacher.repository import TeacherRepository


class TeacherApplicationService:

    def __init__(self, repo: TeacherRepository):
        self.repo = repo

    async def apply(self, user: User, data: TeacherApplicationCreate):
        # тут може бути:
        # - валідація
        # - логування
        # - нотифікації
        # - moderation workflow
        await self.repo.create_teacher(user.id, data)


teacher_application_service = TeacherApplicationService(
    repo=TeacherRepository()
)
