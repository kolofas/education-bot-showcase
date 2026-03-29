from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

import logging

from app.bot.menu import get_main_menu
from app.api.authentication_api import AuthenticationApiClient
from app.configurations.config import API_BASE_URL
from app.database.schemas import UserLoginRequest

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")

router = Router()
auth_client = AuthenticationApiClient(base_url=API_BASE_URL)


class AuthenticationStates(StatesGroup):
    password = State()

async def authenticate_and_handle_response(user_data: dict, message: Message, state: FSMContext):
    """Аутентифицирует пользователя через API и отправляет соответствующее сообщение"""
    user_request = UserLoginRequest(**user_data)
    result = await auth_client.authenticate(user_request)
    logging.info(f"Результат аутентификации: {result}")

    if not result:
        logging.error("Ошибка при аутентификации пользователя")
        await message.answer("Произошла ошибка при входе, попробуйте снова")
        await state.clear()
        return

    if isinstance(result, dict) and result.get("error"):
        await message.answer("Неверные учетные данные. Попробуйте снова")
        await state.clear()
    else:
        token = result.access_token
        if token:
            await message.answer("Вы успешно вошли в систему!", reply_markup=await get_main_menu())
            logging.info(f"[AUTHENTICATION] User {user_data['username']} (ID: {user_data['user_id']} вошел в систему)")
        else:
            await message.answer("Ошибка: не получен токен аутентификации")

        await state.clear()

@router.callback_query(lambda callback_query: callback_query.data == "authorization")
async def start_authentication(callback_query: CallbackQuery, state: FSMContext):
    username = callback_query.from_user.username
    user_id = callback_query.from_user.id
    logging.info(f"Аутентификация пользователя: {username} (ID: {user_id})")

    await state.update_data(username=username, user_id=user_id)
    await callback_query.message.answer("Введите ваш пароль: ")
    await state.set_state(AuthenticationStates.password)
    await callback_query.answer()

@router.message(AuthenticationStates.password)
async def process_password(message: Message, state: FSMContext):
    password = message.text.strip()
    if not password:
        await message.answer("Пароль не может быть пустым. Введите пароль")
        return

    user_data = await state.get_data()
    user_data["password"] = password
    await authenticate_and_handle_response(user_data, message, state)
