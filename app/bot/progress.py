from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.services.progress import get_progress, update_progress
from app.utils.progress_bar import generate_progress_bar


router = Router()


@router.message(Command("show_progress"))
async def show_progress(message: types.Message, db: AsyncSession = get_db()):
    """Показывает текущий прогресс пользователя по уроку."""
    user_id = message.from_user.id
    lesson_id = 1  # Здесь позже можно сделать выбор урока

    progress_entry = await get_progress(user_id, lesson_id, db)
    progress = progress_entry.progress if progress_entry else 0.0

    progress_bar = generate_progress_bar(progress)
    await message.answer(f"Ваш прогресс:\n{progress_bar} ({progress}%)")


@router.message(Command("update_progress"))
async def update_progress_handler(message: types.Message, db: AsyncSession = get_db()):
    """Обновляет прогресс (например, до 50%)"""
    user_id = message.from_user.id
    lesson_id = 1  # Здесь позже можно сделать выбор урока
    new_progress = 50.0  # В дальнейшем можно обновлять на основе действий пользователя

    progress_entry = await update_progress(user_id, lesson_id, new_progress, db)
    if progress_entry:
        progress_bar = generate_progress_bar(progress_entry.progress)
        await message.answer(f"Прогресс обновлен!\n{progress_bar} ({progress_entry.progress}%)")
    else:
        await message.answer("Ошибка при обновлении прогресса. Попробуйте позже.")
