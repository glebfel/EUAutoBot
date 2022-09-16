from aiogram import executor, Dispatcher
from telegram_bot.init_bot import dp
from telegram_bot.handlers import register_client_handlers


async def shutdown(dp: Dispatcher):
    await dp.storage.close()
    await dp.storage.wait_closed()


def run():
    register_client_handlers(dp)
    executor.start_polling(dp, on_shutdown=shutdown)
