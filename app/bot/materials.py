from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging


from app.api.materials_api import MaterialsApiClient
from app.bot.menu import get_main_menu
from app.bot.start import CANCEL_HINT
# from app.api.authentication_api import authenticate_user_to_api
from app.utils.jwt_utils import get_user_token
from app.api.profile_api import ProfileApiClient
from app.configurations.config import API_BASE_URL
from app.database.schemas import MaterialData, MaterialCreateRequest
from app.utils.pagination_utils import (get_page_from_callback, paginate_materials, render_materials_page,
                                    render_materials_message_and_keyboard)

router = Router()
profile_api_client = ProfileApiClient(base_url=API_BASE_URL)
materials_api_client = MaterialsApiClient(base_url=API_BASE_URL)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")

class MaterialForm(StatesGroup):
    title = State()
    description = State()
    file_url = State()


@router.callback_query(lambda callback_query: callback_query.data == "educational_materials")
async def show_materials_list(callback_query: CallbackQuery):
    """Показать список ресурсов пользователя"""
    user_id = callback_query.from_user.id
    token = await profile_api_client.get_user_token(user_id)

    if not token:
        await callback_query.answer("❌ Ошибка авторизации", show_alert=True)
        return

    materials = await materials_api_client.get_all(user_id, token)
    if not materials:
        await callback_query.message.answer("📂 У вас пока нет добавленных ресурсов.")
        await callback_query.answer()
        return

    page = get_page_from_callback(callback_query.data)
    materials_page = paginate_materials(materials, page)

    materials_text = "📚 <b>Ваши ресурсы:</b>\n\n"
    for material in materials:
        materials_text += f"• {material['title']}\n"

    keyboard = render_materials_page(materials_page, total_count=len(materials), page=page)

    await callback_query.message.edit_text(
        materials_text,
        reply_markup=keyboard,
        parse_mode="HTML",
        disable_web_page_preview=True
    )
    await callback_query.answer()


@router.callback_query(F.data.startswith("material_"))
async def show_material_detail(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    token = await profile_api_client.get_user_token(user_id)

    if not token:
        await callback_query.answer("❌ Ошибка авторизации", show_alert=True)
        return

    try:
        material_id = int(callback_query.data.split("_")[1])
    except (IndexError, ValueError):
        await callback_query.answer("❌ Неверный формат данных.")
        return

    material = await materials_api_client.get_by_id(user_id, material_id, token)
    if not material or isinstance(material, dict) and material.get("error"):
        await callback_query.answer("❌ Ресурс не найден или произошла ошибка.")
        return

    # Вывод с гибкой ссылкой
    file_url = material["file_url"]
    link_text = "Перейти к ресурсу" if "http" in file_url and not file_url.lower().endswith(".pdf") else "Скачать"

    text = (
        f"📄 <b>{material['title']}</b>\n"
        f"📜 {material['description']}\n"
        f"🔗 <a href='{file_url}'>{link_text}</a>"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅ Назад к ресурсам", callback_data="educational_materials")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
        ]
    )

    await callback_query.message.edit_text(text,
                                           reply_markup=keyboard,
                                           parse_mode="HTML",
                                           disable_web_page_preview=True)
    await callback_query.answer()

@router.callback_query(lambda callback_query: callback_query.data == "add_material")
async def start_set_state(callback_query: CallbackQuery, state: FSMContext):
    """Запрашиваем заголовок ресурса"""
    await state.set_state(MaterialForm.title)
    await callback_query.message.answer(f"📌 Введите заголовок ресурса: {CANCEL_HINT}")
    await callback_query.answer()

@router.message(MaterialForm.title)
async def process_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(MaterialForm.description)
    await message.answer(f"📝 Введите описание ресурса: {CANCEL_HINT}")

@router.message(MaterialForm.description)
async def process_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(MaterialForm.file_url)
    await message.answer(f"🔗 Отправьте ссылку на файл: {CANCEL_HINT}")

@router.message(MaterialForm.file_url)
async def process_file_url(message: Message, state: FSMContext):
    user_data = await state.get_data()
    title = user_data["title"]
    description = user_data["description"]
    file_url = message.text
    user_id = message.from_user.id

    token = await profile_api_client.get_user_token(user_id)
    if not token:
        await message.answer("❌ Ошибка авторизации. Попробуйте позже.")
        return

    material_data_request = MaterialCreateRequest(
        user_id=user_id,
        title=title,
        description=description,
        file_url=file_url,
        token=token)

    # response = await add_material_api(material_data)
    response = await materials_api_client.add(request=material_data_request)

    if isinstance(response, dict) and "error" in response:
        await message.answer(f"❌ Ошибка при добавлении ресурса: {response['error']}")
    else:
        await message.answer("✅ Ресурс успешно добавлен!\nЧто дальше?", reply_markup=await get_main_menu())

    await state.clear()

@router.callback_query(lambda callback_query: callback_query.data.startswith("educational_materials_page_"))
async def paginate_materials_handler(callback_query: CallbackQuery):
    """Обработка пагинации ресурсов"""
    user_id = callback_query.from_user.id
    token = await profile_api_client.get_user_token(user_id)

    if not token:
        await callback_query.answer("❌ Ошибка авторизации", show_alert=True)
        return

    # materials = await get_materials_list_api(user_id, token)
    materials = await materials_api_client.get_all(user_id, token)
    if not materials:
        await callback_query.message.answer("📂 У вас пока нет добавленных ресурсов.")
        await callback_query.answer()
        return

    page = get_page_from_callback(callback_query.data)
    text, keyboard = render_materials_message_and_keyboard(materials, page)

    await callback_query.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
    await callback_query.answer()
