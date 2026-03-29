from aiogram import Router
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

from app.api.profile_api import ProfileApiClient
from app.bot.menu import get_profile_menu
from app.configurations.config import API_BASE_URL


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")

router = Router()
profile_api_client = ProfileApiClient(base_url=API_BASE_URL)

class UpdateProfileState(StatesGroup):
    waiting_for_username = State()


@router.callback_query(lambda callback_query: callback_query.data == 'my_profile')
async def show_user_profile(callback_query: CallbackQuery):
    """Запрашиваем токен и профиль пользователя"""
    user_id = callback_query.from_user.id
    token = await profile_api_client.get_user_token(user_id)

    if not token:
        await callback_query.answer("Вы не авторизованы. Войдите в систему через /start")
        return

    profile_data = await profile_api_client.fetch_user_profile(token)
    print(f'profile_data: {profile_data}')

    if not profile_data:
        await callback_query.answer("Не удалось загрузить профиль. Попробуйте позже")
        return

    if profile_data.get("error") == "token_expired":
        logging.error(f"Ошибка: fetch_user_profile вернул None для user_id={user_id}")
        await callback_query.answer("Ваш токен истек. Войдите в систему через /start")
        return

    response_text = (
        f"👤 Ваш профиль:\n"
        f"ID: {profile_data.get('user_id')}\n"
        f"Имя: {profile_data.get('login')}\n"
    )

    await callback_query.message.edit_text(response_text, reply_markup=await get_profile_menu())
    await callback_query.answer()

@router.callback_query(lambda callback_query: callback_query.data == "update_profile")
async def update_profile_request(callback_query: CallbackQuery, state: FSMContext):
    """Начало обновления профиля"""
    await callback_query.message.edit_text(
        "✏ Введите новое имя для профиля.\n\nЕсли хотите отменить, напишите /cancel"
    )
    await state.set_state(UpdateProfileState.waiting_for_username)
    await callback_query.answer()

@router.message(UpdateProfileState.waiting_for_username)
async def process_update_profile(message: Message, state: FSMContext):
    """Обновление имени пользователя"""
    new_username = message.text
    user_id = message.from_user.id

    token = await profile_api_client.get_user_token(user_id)

    if not token:
        await message.answer("❌ Вы не авторизованы. Войдите в систему через /start")
        await state.clear()
        return

    result = await profile_api_client.update_user_profile(user_id, new_username, token)

    if result and result.get("message") == "Профиль обновлен":
        await message.answer(f"✅ Ваше имя обновлено на {new_username}.", reply_markup=await get_profile_menu())
    elif result and result.get("error") == "token_expired":
        await message.answer("❌ Ваш токен истек. Войдите в систему через /start")
        await state.clear()
    else:
        await message.answer("❌ Ошибка обновления профиля. Попробуйте позже.")

    await state.clear()


@router.callback_query(lambda callback_query: callback_query.data == "logout")
async def logout_user(callback_query: CallbackQuery):
    """Выход пользователя"""
    user_id = callback_query.from_user.id
    token = await profile_api_client.get_user_token(user_id)

    if not token:
        await callback_query.answer("❌ Вы не авторизованы. Войдите в систему через /start")
        return

    result = await profile_api_client.logout_user(user_id, token)

    if result and result.get("message") == "Вы вышли из системы":
        await callback_query.message.edit_text(
            "✅ Вы вышли из системы. Для входа используйте /start или вернитесь в меню:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🚀 Войти", callback_data="authorization")],
                [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
            ])
        )
    elif result and result.get("error") == "token_expired":
        await callback_query.message.edit_text("❌ Ваш токен истек. Войдите в систему через /start")
    else:
        await callback_query.answer("❌ Ошибка выхода из системы. Попробуйте позже")

@router.callback_query(lambda callback_query: callback_query.data == "reset_token")
async def reset_user_token(callback_query: CallbackQuery):
    """Сброс токена пользователя"""
    user_id = callback_query.from_user.id
    token = await profile_api_client.get_user_token(user_id)

    if not token:
        await callback_query.answer("❌ Вы не авторизованы. Войдите в систему через /start")
        return

    result = await profile_api_client.reset_token_api(user_id, token)

    if result and "access_token" in result:
        await callback_query.message.edit_text(
            "✅ Ваш токен был сброшен.\n\nПожалуйста, авторизуйтесь снова через /start или меню:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🚀 Авторизация", callback_data="authorization")]
            ])
        )
    elif result and result.get("error") == "token_expired":
        await callback_query.message.edit_text("❌ Ваш токен истек. Войдите в систему через /start")
        return
    else:
        await callback_query.answer("❌ Ошибка сброса токена. Попробуйте позже")
