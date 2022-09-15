from aiogram import types, Dispatcher
from aiogram.types import ParseMode
from aiogram.utils.markdown import text, italic
from telegram_bot.init_bot import dp
from telegram_bot.inline_keyboard import start_markup


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.answer(text('Я могу посчитать стоимость авто 🚘 из Германии "под ключ" в РФ.',
                             f'\n\nДля расчета нужна {(italic("ссылка"))} на конкретный авто.',
                             f'\n\nЧто бы начать, нажмите кнопку ниже 👇'),
                        reply_markup=start_markup,
                        parse_mode=ParseMode.MARKDOWN)


def register_client_handlers(dp: Dispatcher):
    dp.register_message_handler(process_start_command)
