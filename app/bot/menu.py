from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.filters import Command
from app.api.authentication_api import AuthenticationApiClient
from app.configurations.config import API_BASE_URL


router = Router()
auth_client = AuthenticationApiClient(base_url=API_BASE_URL)


async def get_main_menu():
    """Главное меню"""
    buttons = [
        [InlineKeyboardButton(text="👤 Мой профиль", callback_data="my_profile")],
        [InlineKeyboardButton(text="📂 Ресурсы", callback_data="educational_materials")],
        [InlineKeyboardButton(text="📤 Добавить ресурс", callback_data="add_material")],
        [InlineKeyboardButton(text="🧩 Предложения", callback_data="school_services")],
        [InlineKeyboardButton(text="🛠️ Добавить предложение", callback_data="add_service")],
        [InlineKeyboardButton(text="🎁 Подарки и бонусы", callback_data="bonuses")],
        [InlineKeyboardButton(text="➕ Добавить бонус", callback_data="add_bonus")],
        [InlineKeyboardButton(text="🌐 Полезные ссылки", callback_data="social_networks")],
        [InlineKeyboardButton(text="🔗 Добавить ссылку", callback_data="add_social_network")]
    ]
    inline_kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return inline_kb

async def get_profile_menu():
    """Меню профиля"""
    buttons = [
        [InlineKeyboardButton(text="Обновить профиль", callback_data="update_profile")],
        [InlineKeyboardButton(text="Выйти из системы", callback_data="logout")],
        [InlineKeyboardButton(text="Сбросить токен", callback_data="reset_token")],
        [InlineKeyboardButton(text="⬅ Назад", callback_data="main_menu")],
    ]
    inline_kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return inline_kb

def get_post_add_service_keyboard():
    """Меню, которое выдается пользователю после добавления предложения"""

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить ещё предложение", callback_data="add_service")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
        ]
    )

@router.message(F.text == "/menu")
async def show_main_menu_for_command(message: Message):
    user_id = message.from_user.id

    if not await auth_client.is_authorized(user_id):
        await message.answer("❌ Вы не авторизованы. Пожалуйста, войдите в систему через команду /start :).")
        return

    keyboard = await get_main_menu()
    await message.answer("📋 Главное меню:", reply_markup=keyboard)

@router.callback_query(lambda callback_query: callback_query.data == "main_menu")
async def show_main_menu_for_back(callback_query: CallbackQuery):
    """Обработчик кнопки главного меню"""
    user_id = callback_query.from_user.id

    if not await auth_client.is_authorized(user_id):
        await callback_query.answer("❌ Вы не авторизованы.", show_alert=True)
        return

    await callback_query.message.edit_text("Выберите действие:", reply_markup=await get_main_menu())
    await callback_query.answer()
