import logging
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from .models import Base  # Используем `Base` из `models.py`
from app.configurations.config import DATABASE_URL, SQL_ECHO

engine = create_async_engine(DATABASE_URL, echo=SQL_ECHO)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")

async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session

async def init_db():
    """
    Initialize the database and create tables if they don't exist.
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logging.info("Таблицы успешно созданы!")
    except Exception as e:
        logging.error(f"Ошибка при создании таблиц: {e}")

async def reset_db():
    """
    Drop all tables and recreate them.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

