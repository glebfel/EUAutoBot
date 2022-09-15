from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram_bot.init_bot import dp

start_btn = InlineKeyboardButton('Рассчитать стоимость', callback_data='calculate')
start_markup = InlineKeyboardMarkup().add(start_btn)


@dp.message_handler(text="calculate")
async def process_calculate_button(callback: CallbackQuery):
    # logic for calculation(parser and etc.)
    await callback.message.answer('')
    pass
