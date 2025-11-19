"""Handlers for profile-related commands."""
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.api_client import ApiClient, ApiClientError
from bot.keyboards import main_menu_keyboard

router = Router()


@router.message(Command("profile"))
async def cmd_profile(message: Message) -> None:
    api_client: ApiClient | None = message.bot.get("api_client")
    if not api_client:
        await message.answer("API клиент не сконфигурирован")
        return

    try:
        profile = await api_client.get_profile(message.from_user.id)
    except ApiClientError as exc:
        await message.answer(f"Не удалось получить профиль: {exc}")
        return

    lines = ["<b>Твой профиль</b>"]
    for key in ("username", "level", "xp", "streak"):
        if value := profile.get(key):
            label = key.capitalize()
            lines.append(f"{label}: {value}")

    if not profile:
        lines.append("Профиль пока пуст. Перейди в приложение и заполни информацию.")

    await message.answer("\n".join(lines), reply_markup=main_menu_keyboard())
