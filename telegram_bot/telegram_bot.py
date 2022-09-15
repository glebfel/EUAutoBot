from aiogram import executor
from telegram_bot.init_bot import dp
from telegram_bot.handlers import register_client_handlers


def run():
    register_client_handlers(dp)
    executor.start_polling(dp)
