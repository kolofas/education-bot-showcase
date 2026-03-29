from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
import logging

from app.bot.menu import get_main_menu
from app.api.registration_api import RegistrationApiClient
from app.configurations.config import API_BASE_URL
from app.database.schemas import UserRegistrationRequest

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")

router = Router()
registration_api_client = RegistrationApiClient(base_url=API_BASE_URL)

class RegistrationStates(StatesGroup):
    password = State()
    confirm_password = State()


async def register_and_handle_response(user_data: dict, message: Message, state: FSMContext):
    """Регистрирует пользователя через API и отправляет соответствующее сообщение"""
    request = UserRegistrationRequest(**user_data)
    result = await registration_api_client.register_user(request)
    logging.info(f'result: {result}')

    if not result:
        logging.error("Ошибка при регистрации пользователя")
        await message.answer(
            "Произошла ошибка при регистрации. Попробуйте снова или вернитесь в главное меню.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔁 Повторить регистрацию", callback_data="registration")],
                [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
            ])
        )
        await state.clear()
        return

    if isinstance(result, dict) and result.get("error") == "Пользователь уже зарегистрирован":
        await message.answer("Вы уже зарегистрированы!", reply_markup=await get_main_menu())
        await state.clear()
    else:
        token = result.get("access_token") # Токен должен быть в ответе

        if token:
            await message.answer(f"Регистрация успешна!\nUsername: {user_data['username']}\n"
                                 f"Пароль успешно установлен!",
                                 reply_markup=await get_main_menu())
            logging.info(f"[REGISTRATION] User {user_data['username']} (ID: {user_data['user_id']}) зарегистрирован")
        else:
            await message.answer(
                "❌ Произошла ошибка: токен не был получен. Попробуйте регистрацию заново или вернитесь в меню.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔁 Повторить регистрацию", callback_data="registration")],
                    [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
                ])
            )

        await state.clear()


async def send_user_already_registered_message(message: Message):
    """Отправляет сообщение о том, что пользователь уже зарегистрирован"""
    await message.answer("Вы уже зарегистрированы!", reply_markup=await get_main_menu())


async def start_registration_flow(callback_query: CallbackQuery, state: FSMContext, username: str, user_id: int):
    """Начинает процесс регистрации, отправляя сообщение для ввода пароля"""
    await state.update_data(username=username, user_id=user_id)

    await callback_query.message.answer(f"Ваш логин {username}. Пожалуйста, введите свой пароль: ")
    await state.set_state(RegistrationStates.password)
    await callback_query.answer()

@router.callback_query(lambda callback_query: callback_query.data == "registration")
async def registration_handler(callback_query: CallbackQuery, state: FSMContext):
    username = callback_query.from_user.username
    user_id = callback_query.from_user.id
    logging.info(f"Полученный user_id: {user_id}, username: {username}")

    # Проверяем, есть ли пользователь в базе
    user_exists = await registration_api_client.check_user_exists(user_id)
    logging.info(f"Проверка на наличие пользователя завершена: {user_exists}")

    # Проверяем, есть ли пользователь в базе
    if user_exists:
        await send_user_already_registered_message(callback_query.message)
        return  # Прекращаем обработку

    logging.info(f"Полученный callback {callback_query.data} от пользователя {username} (ID: {user_id})")
    await start_registration_flow(callback_query, state, username, user_id)

@router.message(RegistrationStates.password)
async def process_password(message: Message, state: FSMContext):
    password = message.text.strip()
    if not password:
        await message.answer("Пароль не может быть пустым. Пожалуйста, введите пароль")
        return
    await state.update_data(password=password)
    await message.answer("Подтвердите свой пароль: ")
    await state.set_state(RegistrationStates.confirm_password) # Переходим в состояние ожидания подтверждения пароля

@router.message(RegistrationStates.confirm_password)
async def process_confirm_password(message: Message, state: FSMContext):
    confirm_password = message.text
    user_data = await state.get_data()  # Получаем данные из FSMContext

    if not confirm_password:
        await message.answer("Пароль подтверждения не может быть пустым. Пожалуйста, повторите попытку регистрации")
        return

    if user_data.get("password") != confirm_password:
        await message.answer("Пароли не совпадают, попробуйте снова")
        return

    await register_and_handle_response(user_data, message, state)
    await state.clear() # Очищаем данные состояния после завершения регистрации
