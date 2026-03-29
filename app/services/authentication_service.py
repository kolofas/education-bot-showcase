from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.models import User
from app.utils.jwt_utils import create_token
from app.database.schemas import UserLoginRequest, UserLoginResponse
from fastapi import HTTPException

import logging


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет соответствие пароля и его хэша"""
    return pwd_context.verify(plain_password, hashed_password)

async def authenticate_user(user_data: UserLoginRequest, db: AsyncSession) -> UserLoginResponse:
    """Функция аутентификации пользователя"""
    try:
        query = select(User).filter(User.user_id == user_data.user_id)
        result = await db.execute(query)
        user = result.scalars().first()

        if user is None:
            logging.info(f"Пользователь с ID {user_data.user_id} не найден")
            raise HTTPException(status_code=401, detail="Неверный пользователь или пароль")

        if not verify_password(user_data.password, user.password_hash):
            logging.info(f"Неверный пароль для пользователя {user_data.user_id}")
            raise HTTPException(status_code=401, detail="Неверный пользователь или пароль")

        access_token = create_token(user.user_id)
        user.access_token = access_token

        db.add(user)
        await db.commit()

        logging.info(f"Пользователь {user.user_id} успешно авторизован")
        return UserLoginResponse.model_validate({
            "access_token": access_token,
        })

    except Exception as e:
        logging.error(f"Ошибка при авторизации: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера")

async def check_user_authentication(user_id: int, db: AsyncSession) -> bool:
    """Проверяет, авторизован ли пользователь (есть ли access_token)"""
    query = select(User).where(User.user_id == user_id)
    result = await db.execute(query)
    user = result.scalars().first()

    if user and user.access_token:
        return True
    return False