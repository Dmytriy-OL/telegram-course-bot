import logging

from app.database.core.paths import AVATAR_DIR, CREATION_COURSES_DIR
from fastapi import UploadFile
import uuid
import shutil
from fastapi import HTTPException

from app.database.crud.web.corses.handle_courses import get_course_by_id, create_video_record


async def save_avatar_to_disk(avatar: UploadFile):
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

    course_folder = CREATION_COURSES_DIR / title / "courses_avatars"
    course_folder.mkdir(parents=True, exist_ok=True)

    file_path = course_folder / file_name

    with file_path.open("wb") as buffer:
        content = await course_avatar.read()
        buffer.write(content)

    return file_name


async def save_video_to_module_folder(video: UploadFile, description: str, course_id: int, module_id: int):
    try:
        course = await get_course_by_id(course_id)
    except ValueError as e:
        logging.error(f"Помилка при отриманні курсу: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    video_path = CREATION_COURSES_DIR / course.title / f"module_{module_id}" / "video"
    video_path.mkdir(parents=True, exist_ok=True)

    file_path = video_path / video.filename

    with file_path.open("wb") as buffer:
        content = await video.read()
        buffer.write(content)

    await create_video_record(
        description=description,
        module_id=module_id,
        video_file=video.filename
    )

    return True
