"""Miscellaneous handlers."""
from aiogram import Router
from aiogram.types import Message

from bot.keyboards import main_menu_keyboard

router = Router()


@router.message()
async def fallback(message: Message) -> None:
    await message.answer(
        "Я понимаю только команды /start, /profile, /domains и /daily."
        "\nИспользуй кнопки, чтобы выбрать действие.",
        reply_markup=main_menu_keyboard(),
    )
