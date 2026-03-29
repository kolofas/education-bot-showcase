import logging

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.models import User
from app.utils.jwt_utils import create_token
from app.database.schemas import (
    UserRegistrationRequest,
    UserCheckResponse,
    MessageResponse,
    TokenResponse
)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")

def hash_password(password: str) -> str:
    """Функция хэширования пароля"""
    return pwd_context.hash(password)

async def is_user_registered(user_id: int, db: AsyncSession) -> UserCheckResponse:
    """Проверяет, зарегистрирован ли пользователь в базе данных"""
    query = select(User).filter(User.user_id == user_id)
    result = await db.execute(query)
    user = result.scalars().first()

    logging.info(f"Пользователь {user_id} найден: {user is not None}")
    return UserCheckResponse(exists=bool(user))

async def register_user_in_database(user_data: UserRegistrationRequest, db: AsyncSession) -> TokenResponse:
    """Функция регистрации пользователя в базу данных бота"""
    try:
        check_result = await is_user_registered(user_data.user_id, db)
        if check_result.exists:
            logging.info(f"Попытка повторной регистрации: {user_data.username} (ID: {user_data.user_id})")
            raise ValueError("Пользователь уже зарегистрирован")

        password_hash = hash_password(user_data.password)
        new_user = User(
            login=user_data.username,
            user_id=user_data.user_id,
            password_hash=password_hash
        )

        access_token = create_token(user_data.user_id) # Генерация токена
        new_user.access_token = access_token # Добавляем токен в модель пользователя

        db.add(new_user)
        await db.commit()

        logging.info(f"Пользователь {user_data.username} успешно зарегистрирован в базе данных")
        return TokenResponse(access_token=access_token)

    except ValueError as ve:
        # Возвращается как HTTP ошибка в вызывающем хендлере, если нужно
        logging.warning(f"Ошибка регистрации: {ve}")
        raise

    except Exception as e:
        logging.error(f"Ошибка при регистрации пользователя: {e}")
        raise RuntimeError("Ошибка при регистрации")

