from aiogram import Dispatcher, executor
from core import custom_logger

from telegram_bot.init_bot import dp, bot
from telegram_bot.handlers import register_client_handlers, register_admin_handlers, register_other_handlers
from databases import start_database


async def on_startup(_):
    await bot.delete_webhook(drop_pending_updates=True)
    # register all handlers
    register_client_handlers(dp)
    register_admin_handlers(dp)
    register_other_handlers(dp)
    # initialize sqlite database
    start_database()
    custom_logger.info('Bot successfully get online!')


async def shutdown(dp: Dispatcher):
    await dp.storage.close()
    await dp.storage.wait_closed()


def run():
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=shutdown)
