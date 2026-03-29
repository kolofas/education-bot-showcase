from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

router = Router()

@router.message()
async def catch_all_unexpected(message: Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state:
        await message.answer("❗ Пожалуйста, завершите текущее действие или отправьте /cancel")
    else:
        await message.answer("🤖 Я вас не понял. Воспользуйтесь /menu")