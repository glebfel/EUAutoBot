from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


start_btn = InlineKeyboardButton('Рассчитать стоимость', callback_data='calculate')
start_markup = InlineKeyboardMarkup().add(start_btn)



