from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# markup for start command
start_btn = InlineKeyboardButton('Рассчитать стоимость', callback_data='calculate')
start_markup = InlineKeyboardMarkup().add(start_btn)

# markup for errors in url input
retry_btn = InlineKeyboardButton('Повторить попытку', callback_data='retry')
cancel_btn = InlineKeyboardButton('Отмена', callback_data='cancel')
error_markup = InlineKeyboardMarkup(row_width=2).add(cancel_btn, retry_btn)


