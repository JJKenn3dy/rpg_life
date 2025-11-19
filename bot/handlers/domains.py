"""/domains command handler."""
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.api_client import ApiClient, ApiClientError
from bot.keyboards import main_menu_keyboard

router = Router()


@router.message(Command("domains"))
async def cmd_domains(message: Message) -> None:
    api_client: ApiClient | None = message.bot.get("api_client")
    if not api_client:
        await message.answer("API клиент не сконфигурирован")
        return

    try:
        domains = await api_client.get_domains(message.from_user.id)
    except ApiClientError as exc:
        await message.answer(f"Не удалось получить домены: {exc}")
        return

    lines = ["<b>Домены развития</b>"]
    for idx, domain in enumerate(domains, start=1):
        title = domain.get("title") or f"Домен {idx}"
        description = domain.get("description", "")
        progress = domain.get("progress")
        item = f"{idx}. {title}"
        if progress is not None:
            item += f" — {progress}%"
        if description:
            item += f"\n{description}"
        lines.append(item)

    if len(lines) == 1:
        lines.append("Домены пока не заданы. Добавь их в веб-приложении.")

    await message.answer("\n\n".join(lines), reply_markup=main_menu_keyboard())
