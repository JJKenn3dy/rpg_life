"""/start command handler."""
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.keyboards import main_menu_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Привет! Я помогу следить за прогрессом и привычками.\n"
        "Нажми на одну из кнопок ниже, чтобы посмотреть профиль, домены или ежедневник.",
        reply_markup=main_menu_keyboard(),
    )
