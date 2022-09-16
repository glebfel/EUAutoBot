from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# markup for start command
start_btn = InlineKeyboardButton('Рассчитать стоимость', callback_data='calculate')
start_markup = InlineKeyboardMarkup().add(start_btn)

# markup for errors in url input
retry_btn = InlineKeyboardButton('Повторить попытку', callback_data='retry')
cancel_btn = InlineKeyboardButton('Отмена', callback_data='cancel')
error_markup = InlineKeyboardMarkup(row_width=2).add(cancel_btn, retry_btn)

# markup for car info output
call_btn = InlineKeyboardButton('Позвонить', callback_data='call')
message_btn = InlineKeyboardButton('Написать', callback_data='message')
another_car_btn = InlineKeyboardButton('Подсчитать другою машину', callback_data='another')
get_more_info_btn = InlineKeyboardButton('Узнать стоимость оформления ЭПТС и СБКТС на этот автомобиль',
                                         callback_data='info')
car_info_markup = InlineKeyboardMarkup(row_width=2).add(call_btn, message_btn).add(get_more_info_btn).add(another_car_btn)

