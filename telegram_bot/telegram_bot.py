from aiogram import executor, Dispatcher
from loguru import logger

from telegram_bot.init_bot import dp
from telegram_bot.handlers import register_client_handlers, register_admin_handlers, register_other_handlers
from databases import create_database, add_password, add_param


async def on_startup(_):
    logger.info('Bot successfully get online!')
    # register all handlers
    register_admin_handlers(dp)
    register_client_handlers(dp)
    register_other_handlers(dp)
    # init and fill db
    create_database()
    add_password('123321')
    add_param('currency_div', 12)
    add_param('dop', 50000)


async def shutdown(dp: Dispatcher):
    await dp.storage.close()
    await dp.storage.wait_closed()


def run():
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=shutdown)
