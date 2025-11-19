"""/daily command handler."""
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.api_client import ApiClient, ApiClientError
from bot.keyboards import main_menu_keyboard

router = Router()


@router.message(Command("daily"))
async def cmd_daily(message: Message) -> None:
    api_client: ApiClient | None = message.bot.get("api_client")
    if not api_client:
        await message.answer("API клиент не сконфигурирован")
        return

    try:
        logs = await api_client.get_daily_logs(message.from_user.id)
    except ApiClientError as exc:
        await message.answer(f"Не удалось получить ежедневник: {exc}")
        return

    lines = ["<b>Ежедневник</b>"]
    for log in logs:
        date = log.get("date", "—")
        mood = log.get("mood")
        text = log.get("note", "")
        entry = f"• {date}"
        if mood:
            entry += f" | настроение: {mood}"
        if text:
            entry += f"\n{text}"
        lines.append(entry)

    if len(lines) == 1:
        lines.append("Записей пока нет. Попробуй добавить заметку в приложении.")

    await message.answer("\n\n".join(lines), reply_markup=main_menu_keyboard())
