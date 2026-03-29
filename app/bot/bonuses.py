from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

from app.api.bonuses_api import BonusApiClient
from app.api.profile_api import ProfileApiClient
from app.configurations.config import API_BASE_URL
from app.database.schemas import BonusCreateRequest
from app.bot.start import CANCEL_HINT

router = Router()
profile_api_client = ProfileApiClient(base_url=API_BASE_URL)
bonuses_api_client = BonusApiClient(base_url=API_BASE_URL)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")

class AddBonus(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_action_text = State()

# Показать список бонусов
@router.callback_query(F.data == "bonuses")
async def show_bonuses(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    token = await profile_api_client.get_user_token(user_id)

    if not token:
        await callback_query.answer("❌ Ошибка авторизации", show_alert=True)
        return

    bonuses = await bonuses_api_client.get_all(user_id, token)
    if not bonuses or isinstance(bonuses, dict) and bonuses.get("error"):
        await callback_query.message.answer("🎁 Сейчас нет активных бонусов.")
        await callback_query.answer()
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"🎁 {b['title']}", callback_data=f"bonus_{b['id']}")]
            for b in bonuses
        ] + [[InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]]
    )

    await callback_query.message.edit_text(
        "🎉 Доступные бонусы и подарки:\n\nВыбери, чтобы узнать подробнее:",
        reply_markup=keyboard
    )
    await callback_query.answer()

# Подробности по бонусу
@router.callback_query(F.data.startswith("bonus_"))
async def bonus_details(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    token = await profile_api_client.get_user_token(user_id)

    try:
        bonus_id = int(callback_query.data.split("_")[1])
    except (IndexError, ValueError):
        await callback_query.answer("❌ Ошибка ID бонуса")
        return

    bonus = await bonuses_api_client.get_by_id(user_id, bonus_id, token)
    if not bonus or isinstance(bonus, dict) and bonus.get("error"):
        await callback_query.answer("❌ Бонус не найден")
        return

    text = (
        f"🎁 <b>{bonus['title']}</b>\n\n"
        f"{bonus['description']}\n\n"
        f"📌 <b>Как получить:</b>\n{bonus['action_text']}"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅ Назад к бонусам", callback_data="bonuses")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
        ]
    )

    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback_query.answer()

@router.callback_query(F.data == "add_bonus")
async def add_bonus_start(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer(f"Введите название бонуса: {CANCEL_HINT}")
    await state.set_state(AddBonus.waiting_for_title)

@router.message(AddBonus.waiting_for_title)
async def process_title(message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer(f"Введите описание бонуса: {CANCEL_HINT}")
    await state.set_state(AddBonus.waiting_for_description)

@router.message(AddBonus.waiting_for_description)
async def process_description(message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer(f"Введите инструкцию (как получить бонус): {CANCEL_HINT}")
    await state.set_state(AddBonus.waiting_for_action_text)

@router.message(AddBonus.waiting_for_action_text)
async def process_action_text(message, state: FSMContext):
    user_data = await state.get_data()
    title = user_data["title"]
    description = user_data["description"]
    action_text = message.text
    user_id = message.from_user.id

    token = await profile_api_client.get_user_token(user_id)
    if not token:
        await message.answer("❌ Ошибка авторизации. Попробуйте позже.")
        return

    bonus_data = BonusCreateRequest(
        user_id=user_id,
        title=title,
        description=description,
        action_text=action_text,
        token=token
    )

    response = await bonuses_api_client.add(bonus_data)

    if isinstance(response, dict) and "error" in response:
        await message.answer(f"❌ Ошибка при добавлении бонуса: {response['error']}")
    else:
        await message.answer("✅ Бонус успешно добавлен!\n\n🎁 А вот и все доступные бонусы:")

        bonuses = await bonuses_api_client.get_all(user_id, token)
        if not bonuses or isinstance(bonuses, dict) and bonuses.get("error"):
            await message.answer("⚠️ Не удалось загрузить бонусы.")
        else:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=f"🎁 {b['title']}", callback_data=f"bonus_{b['id']}")]
                    for b in bonuses
                ] + [[InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]]
            )

            await message.answer("Выберите бонус, чтобы узнать подробнее:", reply_markup=keyboard)

    await state.clear()
