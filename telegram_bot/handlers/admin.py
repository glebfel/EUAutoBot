from aiogram import types, Dispatcher
from aiogram.types import ParseMode
from aiogram.utils.markdown import text

from telegram_bot.init_bot import dp


@dp.message_handler(commands=['moderate'])
async def process_moderate_command(message: types.Message):
    await message.answer(text('Приветствую Вас 👋',
                              f'Вы зашли в режим модератора 🤓',
                              f'Чтобы продолжить наберите секретный ключ для доступа к админ-панели 🗝',
                              sep="\n"),
                         parse_mode=ParseMode.MARKDOWN)


def register_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(process_moderate_command, commands=['moderate'])
