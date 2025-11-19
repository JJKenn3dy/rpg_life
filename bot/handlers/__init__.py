"""Helpers for registering all routers."""
from aiogram import Dispatcher

from . import daily, domains, misc, profile, start


def setup_routers(dp: Dispatcher) -> None:
    for module in (start, profile, domains, daily, misc):
        dp.include_router(module.router)
