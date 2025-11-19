"""Common keyboards used in handlers."""
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=
        [
            [
                KeyboardButton(text="/profile"),
                KeyboardButton(text="/domains"),
            ],
            [
                KeyboardButton(text="/daily"),
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие",
    )
