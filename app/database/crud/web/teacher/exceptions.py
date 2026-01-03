class TeacherApplicationError(Exception):
    pass


class UserAlreadyTeacherError(TeacherApplicationError):
    pass


class UserNotFoundError(TeacherApplicationError):
    pass
