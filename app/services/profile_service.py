from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, Depends
import logging

from app.utils.jwt_utils import create_token
from app.database.schemas import UserProfileResponse, MessageResponse, TokenResetResponse
from app.database.models import User


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")

async def get_user_profile(user_id: int, db: AsyncSession) -> UserProfileResponse:
    """Получение профиля пользователя из базы данных"""
    try:
        query = select(User).filter(User.user_id == user_id)
        result = await db.execute(query)
        user = result.scalars().first()

        if not user:
            logging.info(f"Пользователь с ID {user_id} не найден")
            raise HTTPException(status_code=404, detail="Профиль не найден")

        return UserProfileResponse.model_validate(user)

    except Exception as e:
        logging.error(f"Ошибка получения профиля: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера")

async def get_user_token(user_id: int, db: AsyncSession) -> str:
    """Получение access_token пользователя по user_id"""
    try:
        query = select(User.access_token).filter(User.user_id == user_id)
        result = await db.execute(query)
        token = result.scalar()

        if not token:
            logging.info(f"Токен для пользователя с ID {user_id} не найден")
            raise HTTPException(status_code=404, detail="Токен не найден")

        return token

    except Exception as e:
        logging.error(f"Ошибка получения токена: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера")

async def update_user_profile(user_id: int, username: str, db: AsyncSession) -> MessageResponse:
    """Обновление профиля пользователя"""
    try:
        query = select(User).filter(User.user_id == user_id)
        result = await db.execute(query)
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        user.login = username
        await db.commit()

        return MessageResponse(message="Профиль обновлен")

    except Exception as e:
        logging.error(f"Ошибка обновления профиля: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера")

async def logout_user(user_id: int, db: AsyncSession) -> MessageResponse:
    """Выход пользователя (удаление токена)"""
    try:
        query = select(User).filter(User.user_id == user_id)
        result = await db.execute(query)
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        user.access_token = None
        await db.commit()
        return MessageResponse(message="Вы вышли из системы")

    except Exception as e:
        logging.error(f"Ошибка выхода: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера")

async def reset_user_token(user_id: int, db: AsyncSession) -> TokenResetResponse:
    """Сброс токена пользователя (создание нового)"""
    try:
        query = select(User).filter(User.user_id == user_id)
        result = await db.execute(query)
        user = result.scalars().first()

        if not user:
            logging.error(f"Пользователь {user_id} не найден")
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        else:
            logging.info(f"Найден пользователь: {user.id}, текущий токен: {user.access_token}")

        new_token = create_token(user_id)
        user.access_token = new_token
        await db.commit()

        return TokenResetResponse(access_token=new_token)

    except Exception as e:
        logging.error(f"Ошибка сброса токена: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера")