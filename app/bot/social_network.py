from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

from app.api.profile_api import ProfileApiClient
from app.api.social_network_api import SocialNetworkApiClient
from app.bot.menu import get_main_menu
from app.bot.start import CANCEL_HINT
from app.configurations.config import API_BASE_URL
from app.database.schemas import SocialNetworkCreateRequest

router = Router()
social_api_client = SocialNetworkApiClient(base_url=API_BASE_URL)
profile_api_client = ProfileApiClient(base_url=API_BASE_URL)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")


class SocialNetworkForm(StatesGroup):
    platform = State()
    url = State()
    phone = State()


@router.callback_query(lambda callback_query: callback_query.data == "social_networks")
async def show_social_networks(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    token = await profile_api_client.get_user_token(user_id)

    if not token:
        await callback_query.answer("❌ Ошибка авторизации", show_alert=True)
        return

    networks = await social_api_client.get_all(user_id, token)
    if not networks:
        await callback_query.message.answer("📂 Ссылки пока не добавлены")
        await callback_query.answer()
        return

    text = "🌐 <b>Полезные ссылки:</b>\n\n"
    for net in networks:
        if net.url:
            line = f"• <a href='{net.url}'>{net.platform}</a>"
        else:
            line = f"• <b>{net.platform}</b>"
        if net.phone:
            line += f" – {net.phone}"
        text += line + "\n"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить ссылку", callback_data="add_social_network")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ])

    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML", disable_web_page_preview=True)
    await callback_query.answer()


@router.callback_query(F.data.startswith("social_network_"))
async def show_social_network(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    token = await profile_api_client.get_user_token(user_id)

    try:
        network_id = int(callback_query.data.split("_")[2])
    except (IndexError, ValueError):
        await callback_query.answer("❌ Неверный формат данных")
        return

    network = await social_api_client.get_by_id(user_id, network_id, token)
    if not network or (isinstance(network, dict) and network.get("error")):
        await callback_query.answer("❌ Ссылка не найдена")
        return

    text = f"🌐 <b>{network.platform}</b>\n🔗 {network.url}"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅ Назад", callback_data="social_networks")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ])

    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback_query.answer()


@router.callback_query(lambda callback_query: callback_query.data == "add_social_network")
async def start_add_social_network(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(SocialNetworkForm.platform)
    await callback_query.message.answer(f"🔤 Введите название платформы или ресурса: {CANCEL_HINT}")
    await callback_query.answer()


@router.message(SocialNetworkForm.platform)
async def input_platform(message: Message, state: FSMContext):
    await state.update_data(platform=message.text)
    await state.set_state(SocialNetworkForm.url)
    await message.answer(f"🔗 Введите URL (или отправьте `-`, если не нужно): {CANCEL_HINT}")


@router.message(SocialNetworkForm.url)
async def input_url(message: Message, state: FSMContext):
    url = message.text.strip()
    await state.update_data(url=None if url == "-" else url)
    await state.set_state(SocialNetworkForm.phone)
    await message.answer(f"📞 Введите номер телефона (или отправьте `-`, если не нужно): {CANCEL_HINT}")

@router.message(SocialNetworkForm.phone)
async def input_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    user_data = await state.get_data()
    user_id = message.from_user.id
    token = await profile_api_client.get_user_token(user_id)

    request = SocialNetworkCreateRequest(
        user_id=user_id,
        platform=user_data["platform"],
        url=user_data.get("url"),
        phone=None if phone == "-" else phone,
        token=token
    )

    response = await social_api_client.add(request)

    await state.clear()

    if isinstance(response, dict) and "error" in response:
        await message.answer(f"❌ Ошибка: {response['error']}")
        return

    # ✅ Добавлено успешно, покажем обновлённый список
    networks = await social_api_client.get_all(user_id, token)
    if not networks:
        await message.answer("📂 Ссылки пока не добавлены")
        return

    text = "✅ Ссылка успешно добавлена!\n\n🌐 <b>Полезные ссылки:</b>\n\n"
    for net in networks:
        if net.url:
            line = f"• <a href='{net.url}'>{net.platform}</a>"
        else:
            line = f"• <b>{net.platform}</b>"
        if net.phone:
            line += f" – {net.phone}"
        text += line + "\n"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить ещё", callback_data="add_social_network")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ])

    await message.answer(text, reply_markup=keyboard, parse_mode="HTML", disable_web_page_preview=True)
