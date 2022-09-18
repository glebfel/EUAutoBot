from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# markup for login
exit_btn = InlineKeyboardButton('Выйти из режима модератора 🔚', callback_data='exit_admin')
login_markup = InlineKeyboardMarkup().add(exit_btn)

# markup for authorized user
change_password_btn = InlineKeyboardButton('Изменить секретный ключ 🗝', callback_data='change_password')
change_params_btn = InlineKeyboardButton('Изменить параметры расчётов 🔩', callback_data='change_params')
get_stats_btn = InlineKeyboardButton('Получить статистику использования бота 📊', callback_data='get_stats')
authed_markup = InlineKeyboardMarkup().add(change_password_btn).add(change_params_btn).add(get_stats_btn).add(exit_btn)

# markup for change params
change_currency_div_btn = InlineKeyboardButton('Изменить процент разницы курса €', callback_data='change_currency_div')
change_dop_btn = InlineKeyboardButton('Изменить стоимость оформление СБКТС и ЭПТС', callback_data='change_dop')
return_btn = InlineKeyboardButton('Вернуться 🔙', callback_data='return')
change_params_markup = InlineKeyboardMarkup(row_width=2).add(change_currency_div_btn, change_dop_btn).add(return_btn)

# markup for input params process
cancel_btn = InlineKeyboardButton('Отмена ⛔', callback_data='cancel_admin')
input_values_markup = InlineKeyboardMarkup().add(cancel_btn)