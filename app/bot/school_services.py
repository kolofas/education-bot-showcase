from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

from app.bot.menu import get_post_add_service_keyboard
from app.api.school_service_api import SchoolServiceApiClient
from app.bot.start import CANCEL_HINT
from app.configurations.config import API_BASE_URL
from app.database.schemas import SchoolServiceData, SchoolServiceCreateRequest
from app.utils.jwt_utils import get_user_token
from app.api.profile_api import ProfileApiClient
from app.utils.pagination_utils import (
    get_page_from_callback,
    paginate_services,
    render_services_message_and_keyboard,
)

router = Router()
profile_api_client = ProfileApiClient(base_url=API_BASE_URL)
school_service_api_client = SchoolServiceApiClient(base_url=API_BASE_URL)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")

class ServiceForm(StatesGroup):
    title = State()
    description = State()
    price = State()


@router.callback_query(lambda callback_query: callback_query.data == "school_services")
async def show_services_list(callback_query: CallbackQuery):
    """Показать список предложений"""
    user_id = callback_query.from_user.id
    token = await profile_api_client.get_user_token(user_id)

    if not token:
        await callback_query.answer("❌ Ошибка авторизации", show_alert=True)
        return

    services = await school_service_api_client.get_all(user_id, token)
    if not services:
        await callback_query.message.answer("📂 Предложения пока не добавлены.")
        await callback_query.answer()
        return

    page = get_page_from_callback(callback_query.data)
    text, keyboard = render_services_message_and_keyboard(services, page)
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback_query.answer()


@router.callback_query(F.data.startswith("school_service_"))
async def show_service_detail(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    token = await profile_api_client.get_user_token(user_id)

    try:
        service_id = int(callback_query.data.split("_")[2])
    except (IndexError, ValueError):
        await callback_query.answer("❌ Неверный формат данных.")
        return

    service = await school_service_api_client.get_by_id(user_id, service_id, token)
    if not service or (isinstance(service, dict) and service.get("error")):
        await callback_query.answer("❌ Предложение не найдено.")
        return

    text = (
        f"<b>{service['title']}</b>\n"
        f"{service['description']}\n"
        f"💰 Цена: {service['price']:.2f} ₽"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅ Назад к предложениям", callback_data="school_services")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
        ]
    )

    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback_query.answer()


@router.callback_query(lambda callback_query: callback_query.data == "add_service")
async def start_adding_service(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(ServiceForm.title)
    await callback_query.message.answer(f"📌 Введите название предложения: {CANCEL_HINT}")
    await callback_query.answer()


@router.message(ServiceForm.title)
async def service_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(ServiceForm.description)
    await message.answer(f"📝 Введите описание предложения: {CANCEL_HINT}")


@router.message(ServiceForm.description)
async def service_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(ServiceForm.price)
    await message.answer(f"💰 Введите цену предложения (например, 50.00): {CANCEL_HINT}")


@router.message(ServiceForm.price)
async def service_price(message: Message, state: FSMContext):
    try:
        price = float(message.text)
    except ValueError:
        await message.answer("❌ Пожалуйста, введите корректную цену (например, 50.00).")
        return

    user_data = await state.get_data()
    user_id = message.from_user.id
    token = await profile_api_client.get_user_token(user_id)

    service = SchoolServiceCreateRequest(
        user_id=user_id,
        title=user_data["title"],
        description=user_data["description"],
        price=price,
        token=token
    )

    response = await school_service_api_client.add(request=service)
    if isinstance(response, dict) and "error" in response:
        await message.answer(f"❌ Ошибка при добавлении предложения: {response['error']}")
    else:
        services = await school_service_api_client.get_all(user_id, token)
        if not services:
            await message.answer("📂 Предложения пока не добавлены")
        else:
            page = 1
            text, keyboard = render_services_message_and_keyboard(services, page)

            services_keyboard = keyboard.inline_keyboard + get_post_add_service_keyboard().inline_keyboard
            combined_keyboard = InlineKeyboardMarkup(inline_keyboard=services_keyboard)
            await message.answer(
                f"✅ Предложение успешно добавлено!\n\n{text}",
                reply_markup=combined_keyboard,
                parse_mode="HTML"
            )

    await state.clear()


@router.callback_query(lambda callback_query: callback_query.data.startswith("school_services_page_"))
async def paginate_services_handler(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    token = await profile_api_client.get_user_token(user_id)

    services = await school_service_api_client.get_all(user_id, token)
    if not services:
        await callback_query.message.answer("📂 Предложения пока не добавлены.")
        await callback_query.answer()
        return

    page = get_page_from_callback(callback_query.data)
    text, keyboard = render_services_message_and_keyboard(services, page)

    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback_query.answer()
