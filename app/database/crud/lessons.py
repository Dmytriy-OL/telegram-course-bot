from datetime import datetime, timedelta

from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.sql.expression import or_, and_

from app.database.core.models import SessionLocal, Lesson, Enrollment, Administrator, LessonType


async def get_lessons_for_teacher_and_optional_student(teacher_id: int, student_id: int | None = None) -> list[Lesson]:
    async with SessionLocal() as session:
        today = datetime.today()
        this_monday = datetime.combine(today - timedelta(days=today.weekday()), datetime.min.time())
        next_sunday = this_monday + timedelta(days=13, hours=23, minutes=59, seconds=59)

        stmt = (
            select(Lesson)
            .join(Enrollment) if student_id is not None else select(Lesson)
        )

        stmt = stmt.where(
            Lesson.datetime >= this_monday,
            Lesson.datetime <= next_sunday,
            Lesson.teacher_id == teacher_id
        )

        if student_id is not None:
            stmt = stmt.where(Enrollment.user_tg_id == student_id)

        stmt = stmt.options(
            joinedload(Lesson.administrator),
            joinedload(Lesson.enrollments).joinedload(Enrollment.user)
        )

        result = await session.execute(stmt)
        return result.unique().scalars().all()


async def create_lesson(title: str, year: int, month: int, day: int, hour: int, minute: int,
                        type_lesson: LessonType,
                        places: int, teacher_id_tg: int, freely: bool = True) -> Lesson:
    """Функція яка створює нове заняття"""
    async with SessionLocal() as session:
        result = await session.execute(select(Administrator).where(Administrator.tg_id == teacher_id_tg))
        administrator = result.scalars().first()

        if not administrator:
            raise ValueError("❌ Адміністратор з таким telegram_id не знайдений у базі.")

        lesson_datetime = datetime(year, month, day, hour, minute)
        lesson = Lesson(
            title=title,
            datetime=lesson_datetime,
            type_lesson=type_lesson,
            freely=freely,
            places=places,
            teacher_id=administrator.id
        )
        session.add(lesson)
        await session.commit()
        print("📌 Заняття додано в базу!")
        await session.refresh(lesson)
        return lesson


async def find_activities_by_date(year: int, month: int, day: int) -> list[Lesson]:
    async with SessionLocal() as session:
        start_date = datetime(year, month, day, 0, 0, 0)
        end_date = datetime(year, month, day, 23, 59, 59)
        print(f"Шукаємо заняття від {start_date} до {end_date}")
        result = await session.execute(
            select(Lesson).options(selectinload(Lesson.administrator)).where(and_(Lesson.datetime >= start_date,
                                                                                  Lesson.datetime <= end_date)))
        lessons = result.scalars().all()
        if lessons:
            for lesson in lessons:
                lesson.type_lesson = "Онлайн" if lesson.type_lesson == LessonType.ONLINE else "Офлайн"
                print(f"Заняття: {lesson.title}\nЧас: {lesson.datetime}\nТип: {lesson.type_lesson}")
            return lessons
        else:
            print("Заняття на цей день відсутні")
            return []


async def lesson_records_display(tg_id: int) -> list[Enrollment]:
    async with SessionLocal() as session:
        result = await session.execute(
            select(Enrollment)
            .where(Enrollment.user_tg_id == tg_id)
            .options(
                joinedload(Enrollment.lesson).joinedload(Lesson.administrator)
            )
        )
        records = result.scalars().all()
        return records


async def cancel_record_lessons(lesson_id: int) -> Enrollment | None:
    async with SessionLocal() as session:
        result = await session.execute(
            select(Enrollment).where(Enrollment.id == lesson_id).options(joinedload(Enrollment.lesson))
        )
        record = result.scalars().first()
        if record:
            lesson = record.lesson
            print(f"Запис {lesson.title},скасовоно")
            lesson.places += 1
            await session.delete(record)
            if not lesson.freely:
                lesson.freely = True

            await session.commit()
            return record
        else:
            print("Запис ненайдено")
        return None


async def enroll_student_to_lesson(lesson_id: int, user_tg_id: int, full_name: str) -> str | None:  # !!! return
    async with SessionLocal() as session:
        enrollment = Enrollment(user_tg_id=user_tg_id, lesson_id=lesson_id, full_name=full_name)
        result = await session.execute(select(Lesson).where(Lesson.id == lesson_id))
        lesson = result.scalar_one_or_none()
        if lesson:
            if lesson.places > 0:
                lesson.places -= 1
                if lesson.places == 0:
                    lesson.freely = False
            else:
                return "Місця на заняття більше не доступні."
        session.add(enrollment)

        await session.commit()


async def remove_enrollment_for_student(lessons_id: int, student_id: int | None = None,
                                        student_record: int | None = None) -> None:
    async with SessionLocal() as session:
        stmt = (
            select(Lesson)
            .where(Lesson.id == lessons_id)
            .options(joinedload(Lesson.enrollments))
        )
        result = await session.execute(stmt)

        lesson = result.unique().scalar_one_or_none()

        if lesson:
            for ent in lesson.enrollments:
                if (student_id is not None and ent.user_tg_id == student_id) or \
                        (student_record is not None and ent.id == student_record):
                    lesson.places += 1
                    print(f"Заняття: {lesson.title} - вільних місць стало {lesson.places}")
                    print(f"❌ Видаляю: {ent.full_name} ({ent.user_tg_id}) з '{lesson.title}'")
                    await session.delete(ent)
            await session.commit()


async def get_enrollments_for_two_weeks() -> list[Enrollment]:
    async with SessionLocal() as session:
        today = datetime.today()
        weekday = today.weekday()  # 0 = Monday

        this_monday = today - timedelta(days=weekday)
        next_sunday = this_monday + timedelta(days=13)

        result = await session.execute(
            select(Enrollment)
            .join(Enrollment.lesson)
            .options(joinedload(Enrollment.lesson), joinedload(Enrollment.user))
            .where(Lesson.datetime >= this_monday)
            .where(Lesson.datetime <= next_sunday)
        )

        enrollments = result.scalars().all()

        return enrollments
