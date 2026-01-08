from app.database.crud.web.services.teacher_application import TeacherApplicationService, ProfileService
from app.database.crud.web.teacher.repository import TeacherRepository
from app.database.crud.web.user.repository import UserRepository


def get_profile_service() -> ProfileService:
    return ProfileService(
        repo=UserRepository()
    )
