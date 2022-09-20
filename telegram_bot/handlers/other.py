from aiogram import Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils.markdown import text
from telegram_bot.init_bot import dp


@dp.message_handler()
async def process_other_commands(message: types.Message):
    await message.answer(text("Не могу распознать введенную команду 🧐❗",
                              "\nДля просмотра доступных команд воспользуйтесь /help 🧾"),
                         parse_mode=ParseMode.MARKDOWN)


def register_other_handlers(dp: Dispatcher):
    dp.register_message_handler(process_other_commands)
