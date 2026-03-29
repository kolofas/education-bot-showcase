from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext

from app.bot.menu import get_main_menu

router = Router()

@router.message(Command("start"))
async def start(message: Message) -> None:
    buttons = [
        [InlineKeyboardButton(text='Регистрация', callback_data='registration')],
        [InlineKeyboardButton(text='Авторизация', callback_data='authorization')]
    ]
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(text="Привет! Чтобы продолжить надо зарегистрироваться или войти в систему 🤖",
                         reply_markup=inline_keyboard)

@router.message(Command("cancel"))
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("❌ Нет активного действия для отмены.")
        return

    await state.clear()
    await message.answer("✅ Действие отменено. Возвращаю вас в главное меню...",
                         reply_markup=await get_main_menu())

CANCEL_HINT = "\n\nЕсли хотите отменить действие — отправьте /cancel"