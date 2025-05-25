from app.database.models import engine,Base
import asyncio
import os


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Таблиці створено!")


if __name__ == "__main__":
    asyncio.run(create_tables())
