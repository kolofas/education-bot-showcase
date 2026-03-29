import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select


async def get_progress(user_id: int, lesson_id: int, db: AsyncSession) -> Progress | None:
    """Получает запись прогресса пользователя, если она существует."""
    result = await db.execute(
        select(Progress).filter(Progress.user_id == user_id, Progress.lesson_id == lesson_id)
    )
    scalars_result = await result.scalars()  # Разворачиваем вызовы
    return scalars_result.first()  # Теперь first() вызывается у уже готового результата

async def create_progress(user_id: int, lesson_id: int, progress: float, db: AsyncSession) -> Progress:
    """Создаёт новую запись прогресса."""
    progress_entry = Progress(
        user_id=user_id,
        lesson_id=lesson_id,
        progress=progress,
        updated_at=datetime.utcnow()
    )
    db.add(progress_entry)
    return progress_entry

async def update_progress_entry(progress_entry: Progress, progress: float) -> None:
    """Обновляет существующую запись прогресса."""
    progress_entry.progress = progress
    progress_entry.updated_at = datetime.utcnow()

async def update_progress(user_id: int, lesson_id: int, progress: float, db: AsyncSession) -> Progress | None:
    """Обновляет или создаёт запись прогресса пользователя."""
    try:
        progress_entry = await get_progress(user_id, lesson_id, db)

        if progress_entry:
            await update_progress_entry(progress_entry, progress)
        else:
            progress_entry = await create_progress(user_id, lesson_id, progress, db)

        await db.commit()
        logging.info(f"Прогресс обновлен: {user_id} - Урок {lesson_id} - {progress}%")
        return progress_entry

    except SQLAlchemyError as e:
        await db.rollback()
        logging.error(f"Ошибка при обновлении прогресса: {e}")
        return None
