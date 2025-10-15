from app.database.core.paths import AVATAR_DIR, AVATAR_COURSES_DIR
from fastapi import UploadFile
import uuid
import shutil


async def save_image_to_disk_and_db(avatar: UploadFile):
    ext = avatar.filename.split(".")[-1].lower()
    file_name = f"{uuid.uuid4()}.{ext}"
    file_path = AVATAR_DIR / f"{file_name}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(avatar.file, buffer)

    return file_name


async def save_image_to_course_folder(course_avatar: UploadFile, title: str):
    _, ext = course_avatar.filename.rsplit(".", 1)
    ext = ext.lower()

    allowed_ext = {"jpg", "jpeg", "png", "webp"}
    if ext not in allowed_ext:
        raise ValueError(f"Unsupported image format: {ext}")

    file_name = f"{title}.{ext}"

    course_folder = AVATAR_COURSES_DIR / title
    course_folder.mkdir(parents=True, exist_ok=True)

    file_path = course_folder / file_name

    with file_path.open("wb") as buffer:
        content = await course_avatar.read()
        buffer.write(content)

    return file_name
