import os
import jwt
import datetime
from dotenv import load_dotenv
from fastapi import HTTPException
from aiogram.types import CallbackQuery
from app.api.authentication_api import AuthenticationApiClient
from app.configurations.config import API_BASE_URL

load_dotenv()

JWT_SECRET = os.getenv('JWT_SECRET')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM')
JWT_EXPIRATION_DELTA = int(os.getenv("JWT_EXPIRATION_MINUTES", 60))

auth_client = AuthenticationApiClient(base_url=API_BASE_URL)

def create_token(user_id: int):
    """Создает JWT токен и возвращает его"""
    expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=JWT_EXPIRATION_DELTA)
    payload = {
        "user_id": user_id,
        "exp": expiration
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def decode_token(token: str):
    """Декодирует JWT и проверяет срок его действия"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        exp_timestamp = payload.get("exp")

        if exp_timestamp:
            exp_datetime = datetime.datetime.utcfromtimestamp(exp_timestamp)
            if exp_datetime < datetime.datetime.utcnow():
                raise HTTPException(status_code=401, detail="Токен истек, авторизуйтесь снова")

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Токен истек, авторизуйтесь снова")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Неверный токен")


def verify_token(authorization: str, user_id: int) -> None:
    """Проверяет валидность токена и соответствие user_id"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Токен не предоставлен")

    token = authorization.replace("Bearer", "").strip()
    decoded_token = decode_token(token)

    if decoded_token is None:
        raise HTTPException(status_code=401, detail="Неверный или истекший токен")

    if decoded_token["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Доступ запрещен")


async def get_user_token(callback_query: CallbackQuery) -> str | None:
    """Проверяет авторизацию пользователя и возвращает токен или None"""
    user_id = callback_query.from_user.id
    token = await auth_client.get_token(user_id)

    if not token:
        await callback_query.answer("❌ Вы не авторизованы. Войдите в систему через /start")
        return None

    return token
