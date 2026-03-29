import logging

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

MATERIALS_PER_PAGE = 5

def get_page_from_callback(data: str) -> int:
    try:
        return int(data.split("_")[-1])
    except (ValueError, IndexError):
        return 0

def paginate_materials(materials: list, page: int) -> list:
    if not isinstance(materials, list):
        logging.error(f"[Pagination] Ожидался список ресурсов, но пришло: {type(materials)} — {materials}")
        return []

    start = page * MATERIALS_PER_PAGE
    end = start + MATERIALS_PER_PAGE

    return materials[start:end]

def render_materials_page(materials_page: list, total_count: int, page: int) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=materials["title"], callback_data=f'material_{materials["id"]}')]
        for materials in materials_page
    ]

    navigation = []
    if page > 0:
        navigation.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"educational_materials_page_{page - 1}"))
    if (page + 1) * MATERIALS_PER_PAGE < total_count:
        navigation.append(InlineKeyboardButton(text="Вперёд ▶️", callback_data=f"educational_materials_page_{page + 1}"))

    if navigation:
        buttons.append(navigation)

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def render_materials_message_and_keyboard(materials: list, page: int) -> tuple[str, InlineKeyboardMarkup]:
    if not isinstance(materials, list):
        materials = []

    materials_page = paginate_materials(materials, page)
    total_pages = (len(materials) + MATERIALS_PER_PAGE - 1) // MATERIALS_PER_PAGE

    text = f"📚 <b>Ваши ресурсы</b> (Страница {page + 1} из {max(total_pages, 1)}):\n\n"
    for material in materials_page:
        text += f"• {material['title']}\n"

    keyboard = render_materials_page(materials_page=materials_page, total_count=len(materials), page=page)

    return text, keyboard


def paginate_services(services: list, page: int) -> list:
    if not isinstance(services, list):
        logging.error(f"[Pagination] Ожидался список, но пришло: {type(services)} — {services}")
        return []

    start = page * MATERIALS_PER_PAGE
    end = start + MATERIALS_PER_PAGE
    return services[start:end]

def render_services_page(services_page: list, total_count: int, page: int) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=service["title"], callback_data=f'school_service_{service["id"]}')]
        for service in services_page
    ]

    navigation = []
    if page > 0:
        navigation.append(
            InlineKeyboardButton(text="◀️ Назад", callback_data=f"school_services_page_{page - 1}")
        )
    if (page + 1) * MATERIALS_PER_PAGE < total_count:
        navigation.append(
            InlineKeyboardButton(text="Вперёд ▶️", callback_data=f"school_services_page_{page + 1}")
        )

    if navigation:
        buttons.append(navigation)

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def render_services_message_and_keyboard(services: list, page: int) -> tuple[str, InlineKeyboardMarkup]:
    if not isinstance(services, list):
        services = []
    services_page = paginate_services(services, page)
    total_pages = (len(services) + MATERIALS_PER_PAGE - 1) // MATERIALS_PER_PAGE

    text = f"🧩 <b>Предложения</b> (Страница {page + 1} из {max(total_pages, 1)}):\n\n"
    for service in services_page:
        text += f"• {service['title']} — {service['price']:.2f} ₽\n"

    keyboard = render_services_page(services_page, total_count=len(services), page=page)
    return text, keyboard
