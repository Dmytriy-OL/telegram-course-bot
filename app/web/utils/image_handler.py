from app.database.core.paths import AVATAR_DIR
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
