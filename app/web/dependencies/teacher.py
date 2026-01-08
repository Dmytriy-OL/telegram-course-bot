from app.database.crud.web.services.teacher_application import TeacherApplicationService
from app.database.crud.web.teacher.repository import TeacherRepository


def get_teacher_application_service() -> TeacherApplicationService:
    return TeacherApplicationService(
        repo=TeacherRepository()
    )
