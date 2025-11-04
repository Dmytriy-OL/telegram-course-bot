import logging

from sqlalchemy import update, delete, and_
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.database.core.models import Courses, Administrator, Module, Task, Answer, CourseAvatar, VideoModule
from app.database.core.models import SessionLocal

from datetime import date


async def create_course(title: str, save_image: str, price: int, caption: str, lesson_count: int, teacher_id: int):
    async with SessionLocal() as session:
        course_avatar = CourseAvatar(file_name=save_image)

        add_course = Courses(title=title, price=price, caption=caption, lesson_count=lesson_count,
                             teacher_id=teacher_id, avatar=course_avatar)
        session.add(add_course)
        await session.commit()
        return True


async def all_courses():
    async with SessionLocal() as session:
        result = await session.execute(select(Courses).options(selectinload(Courses.teacher),
                                                               selectinload(Courses.avatar)))
        return result.scalars().all()


async def create_module(title: str, notes: str, order: int, is_active: bool, course_id: int):
    async with SessionLocal() as session:
        add_module = Module(title=title, notes=notes, order=order,
                            is_active=is_active, course_id=course_id)
        try:
            session.add(add_module)
            await session.commit()
            await session.refresh(add_module)
            return add_module.id
        except Exception as e:
            await session.rollback()
            raise e


async def create_task_for_module(question: str, filename_img: str, module_id: int) -> int:
    async with SessionLocal() as session:
        add_task = Task(question=question, filename_img=filename_img, module_id=module_id, )
        try:
            session.add(add_task)
            await session.commit()
            await session.refresh(add_task)
            return add_task.id
        except Exception as e:
            await session.rollback()
            raise e


async def generate_answer(text: str, is_correct: bool, task_id: int):
    async with SessionLocal() as session:
        add_answer_to_question = Answer(text=text, is_correct=is_correct, task_id=task_id)
        try:
            session.add(add_answer_to_question)
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e


async def create_video_url(title: str, module_id: int, video_url: str | None = None, video_file: str | None = None):
    async with SessionLocal() as session:
        create_video = VideoModule(description=title, video_url=video_url, video_file=video_file,
                                   module_id=module_id)
        try:
            session.add(create_video)
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e


async def get_course_by_id(id_course: int) -> Courses:
    async with SessionLocal() as session:
        result = await session.execute(
            select(Courses).where(Courses.id == id_course)
        )
        course = result.scalar_one_or_none()

        if not course:
            raise ValueError("Сталася помилка: курс не знайдено")

        return course


async def create_video_record(description: str, module_id: int, video_url: str | None = None,
                              video_file: str | None = None):
    async with SessionLocal() as session:
        create_video = VideoModule(description=description, video_url=video_url, video_file=video_file,
                                   module_id=module_id)
        try:
            session.add(create_video)
            await session.commit()
        except Exception as e:
            await session.rollback()
            logging.error(f"Помилка при записі відео в базу: {e}")
            raise


async def get_used_lessons_for_course(course_id: int) -> list[int]:
    async with SessionLocal() as session:
        result = await session.execute(
            select(Module.order).where(Module.course_id == course_id)
        )
        used_orders = [row[0] for row in result.all()]
        return used_orders
