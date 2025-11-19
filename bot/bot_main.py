"""Entry point for the Telegram bot."""
from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage

from bot.api_client import ApiClient
from bot.config import settings
from bot.handlers import setup_routers


async def set_bot_commands(bot: Bot) -> None:
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Начать работу"),
            BotCommand(command="profile", description="Показать профиль"),
            BotCommand(command="domains", description="Домены развития"),
            BotCommand(command="daily", description="Ежедневник"),
        ]
    )


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    bot = Bot(
        token=settings.BOT_TOKEN.get_secret_value(),
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    dp = Dispatcher(storage=MemoryStorage())

    api_client = ApiClient(
        str(settings.BACKEND_URL),
        timeout=settings.HTTP_TIMEOUT,
    )
    bot["api_client"] = api_client

    setup_routers(dp)
    await set_bot_commands(bot)

    try:
        await dp.start_polling(bot)
    finally:
        await api_client.close()


if __name__ == "__main__":
    asyncio.run(main())
