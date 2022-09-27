from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# markup for start command
start_btn = InlineKeyboardButton('Рассчитать стоимость 📈', callback_data='calculate')
start_markup = InlineKeyboardMarkup().add(start_btn)

# markup for car info output
call_btn = InlineKeyboardButton('Позвонить 📞', callback_data='call')
message_btn = InlineKeyboardButton('Написать в WhatsApp 📲', url='https://api.whatsapp.com/send/?phone=79111938955')
another_car_btn = InlineKeyboardButton('Подсчитать другую машину 🚙', callback_data='another')
get_more_info_btn = InlineKeyboardButton('Узнать стоимость оформления ЭПТС и СБКТС на этот автомобиль',
                                         url='https://api.whatsapp.com/send/?phone=79111938955')
car_info_markup = InlineKeyboardMarkup(row_width=2).add(call_btn, message_btn).add(get_more_info_btn).add(
    another_car_btn)

# markup for get phone
get_phone_markup = InlineKeyboardMarkup().add(another_car_btn)

# markup for car error
car_error_markup = InlineKeyboardMarkup().add(another_car_btn)

# markup for basic errors
retry_btn = InlineKeyboardButton('Повторить попытку 🔄', callback_data='retry')
error_markup = InlineKeyboardMarkup().add(retry_btn)