"""/daily command handler."""
from __future__ import annotations

import asyncio

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
        logs, finances = await asyncio.gather(
            api_client.get_daily_logs(message.from_user.id),
            api_client.get_finances(message.from_user.id),
        )
    except ApiClientError as exc:
        await message.answer(f"Не удалось получить ежедневник: {exc}")
        return

    lines = ["<b>Ежедневник</b>"]
    has_logs = False
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
        has_logs = True

    if not has_logs:
        lines.append("Записей пока нет. Попробуй добавить заметку в приложении.")

    lines.append("")
    lines.append("<b>Финансы</b>")
    has_finances = False
    for record in finances:
        date = record.get("date", "—")
        amount = record.get("amount")
        currency = record.get("currency", "")
        category = record.get("category")
        note = record.get("note", "")

        entry = f"• {date}"
        if amount is not None:
            amount_str = str(amount)
            if currency:
                amount_str += f" {currency}"
            entry += f" | сумма: {amount_str}"
        if category:
            entry += f" | категория: {category}"
        if note:
            entry += f"\n{note}"
        lines.append(entry)
        has_finances = True

    if not has_finances:
        lines.append("Финансовых записей пока нет. Добавь траты в приложении.")

    await message.answer("\n\n".join(lines), reply_markup=main_menu_keyboard())
