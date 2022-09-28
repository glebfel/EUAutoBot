import datetime
import pathlib

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ParseMode, CallbackQuery
from aiogram.utils.markdown import text, bold, italic

from core import custom_logger
from telegram_bot.keyboards import (login_markup, authed_markup,
                                    change_params_markup, input_values_markup, show_params_markup, show_stats_markup,
                                    start_markup)
from telegram_bot.init_bot import dp
from databases import *
from telegram_bot.generate_csv_from_stats import create_csv

# csv file directory
DIR_PATH = str(pathlib.Path(__file__).parent.parent)


class FSMLogin(StatesGroup):
    password = State()


class FSMChangePassword(StatesGroup):
    password = State()


class FSMChangeParams(StatesGroup):
    param = State()
    value = State()


class FSMSpamUsers(StatesGroup):
    message = State()


@dp.message_handler(commands=['moderate'], state=None)
async def process_moderate_command(message: types.Message):
    custom_logger.info('/moderate command invoked')
    if check_user(message.from_user.id):
        update_user_last_auth(message.from_user.id)
        await message.answer(text('Приветствую Вас 👋',
                                  f'Вы уже были ранее авторизованы 🔓',
                                  '\nВыберите Ваши дальнейшие действия с помощью кнопок снизу 👇',
                                  sep="\n"),
                             parse_mode=ParseMode.MARKDOWN,
                             reply_markup=authed_markup
                             )
    else:
        await FSMLogin.password.set()
        await message.answer(text('Приветствую Вас 👋',
                                  f'Вы зашли в режим модератора 📝',
                                  f'\nЧтобы продолжить наберите пароль 🔑 для доступа к админ-панели',
                                  sep="\n"),
                             parse_mode=ParseMode.MARKDOWN,
                             reply_markup=login_markup)


@dp.message_handler(state=FSMLogin.password)
async def process_password_input(message: types.Message, state: FSMContext):
    if check_password(message.text):
        add_user(message.from_user.id)
        await message.answer(text('Вы успешно авторизованы 🔓',
                                  'Выберите Ваши дальнейшие действия с помощью кнопок снизу 👇',
                                  sep="\n\n"),
                             parse_mode=ParseMode.MARKDOWN,
                             reply_markup=authed_markup)
        await state.finish()
        await state.reset_state()
    else:
        await message.answer(text('📛 Введён неверный пароль 📛',
                                  'Повторите попытку 🔄',
                                  sep="\n"),
                             parse_mode=ParseMode.MARKDOWN,
                             reply_markup=login_markup)


@dp.callback_query_handler(text='change_password', state=None)
async def process_change_password_button(callback: CallbackQuery):
    await FSMChangePassword.password.set()
    await callback.message.answer(text('Введите желаемый пароль 👇⌨'),
                                  parse_mode=ParseMode.MARKDOWN,
                                  reply_markup=input_values_markup)
    await callback.answer()


@dp.message_handler(state=FSMChangePassword.password)
async def process_password_input(message: types.Message, state: FSMContext):
    update_password(message.text)
    await message.answer(text('Новый пароль успешно сохранён 👏'),
                         parse_mode=ParseMode.MARKDOWN,
                         reply_markup=authed_markup)
    custom_logger.warning('Password has been changed!')
    await state.finish()
    await state.reset_state()


@dp.callback_query_handler(text='show_params')
async def process_show_params_button(callback: CallbackQuery):
    currency_div = get_param_value('exchange_div')
    dop = get_param_value('dop')
    await callback.message.answer(text(f'{bold("Стоимость оформление СБКТС и ЭПТС")}: {dop}₽',
                                       f'{bold("Процент разницы курса ЦБ и обменников")}: {currency_div}%',
                                       sep="\n"
                                       ),
                                  parse_mode=ParseMode.MARKDOWN,
                                  reply_markup=show_params_markup)
    await callback.answer()


@dp.callback_query_handler(text='change_params', state=None)
async def process_change_params_button(callback: CallbackQuery):
    await FSMChangeParams.param.set()
    await callback.message.answer(text('Выберите параметр, значение которого хотели бы изменить, с помощью кнопок '
                                       'ниже 👇'),
                                  parse_mode=ParseMode.MARKDOWN,
                                  reply_markup=change_params_markup)
    await callback.answer()


@dp.callback_query_handler(text='change_exchange_div', state=FSMChangeParams.param)
async def process_change_exchange_div_button(callback: CallbackQuery, state=FSMContext):
    await callback.message.answer(text('Введите число 👇⌨'),
                                  parse_mode=ParseMode.MARKDOWN,
                                  reply_markup=input_values_markup)
    await callback.answer()
    async with state.proxy() as data:
        data['param'] = 'exchange_div'
    await FSMChangeParams.next()


@dp.callback_query_handler(text='change_dop', state=FSMChangeParams.param)
async def process_change_change_dop_button(callback: CallbackQuery, state=FSMContext):
    await callback.message.answer(text('Введите число 👇⌨'),
                                  parse_mode=ParseMode.MARKDOWN,
                                  reply_markup=input_values_markup)
    await callback.answer()
    async with state.proxy() as data:
        data['param'] = 'dop'
    await FSMChangeParams.next()


@dp.message_handler(state=FSMChangeParams.value)
async def process_param_value(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            value = int(message.text)
            update_param(data['param'], value)
            await message.answer(text('Значение сохранено ✅'),
                                 parse_mode=ParseMode.MARKDOWN,
                                 reply_markup=authed_markup)
            custom_logger.warning(f'{data["param"]} param has been changed!')
        await state.finish()
        await state.reset_state()
    except (TypeError, ValueError):
        await message.answer(text('🛑 Некорректное значение 🛑',
                                  'Требуется ввести целочисленное значение (больше нуля)',
                                  'Повторите попытку 🔄',
                                  sep="\n\n"),
                             parse_mode=ParseMode.MARKDOWN,
                             reply_markup=input_values_markup)


@dp.callback_query_handler(text='get_stats')
async def process_get_stats_button(callback: CallbackQuery):
    # create csv file
    create_csv()
    # make formatted output
    count_overall_usage = get_start_command_usage_overall()
    count_today_usage = get_start_command_usage_overall(from_timespan=datetime.date.today())
    count_unique_users_overall = get_number_of_unique_users()
    count_unique_users_today = get_number_of_unique_users(from_timespan=datetime.date.today())
    count_car_calculation_overall = get_car_calculation_count_overall()
    count_car_calculation_today = get_car_calculation_count_overall(from_timespan=datetime.date.today())
    count_feedback_request_overall = get_feedback_usage_count_overall()
    count_feedback_request_today = get_feedback_usage_count_overall(from_timespan=datetime.date.today())
    await callback.message.answer(text(bold('Статистика использования бота 📊'),
                                       bold("\nЗа сегодня:"),
                                       f"{italic('Количество использований бота:')} {count_today_usage}",
                                       f"{italic('Количество уникальных пользователей:')} {count_unique_users_today}",
                                       f"{italic('Количество проведённых расчётов стоимости авто:')} {count_car_calculation_today}",
                                       str(italic(
                                           f'Количество запросов на получение обратной связи (звонки): {count_feedback_request_today}')).replace(
                                           '\\', ''),
                                       bold("\nЗа всё время:"),
                                       f"{italic('Количество использований бота:')} {count_overall_usage}",
                                       f"{italic('Количество уникальных пользователей:')} {count_unique_users_overall}",
                                       f"{italic('Количество проведённых расчётов стоимости авто:')} {count_car_calculation_overall}",
                                       str(italic(
                                           f'Количество запросов на получение обратной связи (звонки): {count_feedback_request_overall}')).replace(
                                           '\\', ''),
                                       sep='\n'),
                                  parse_mode=ParseMode.MARKDOWN,
                                  reply_markup=show_stats_markup)
    await callback.answer()


@dp.callback_query_handler(text='get_csv')
async def process_download_csv_button(callback: CallbackQuery):
    await callback.message.reply_document(open(DIR_PATH + '/stats.csv', 'rb'), reply_markup=show_params_markup)
    await callback.answer()


@dp.callback_query_handler(text='spam', state=None)
async def process_spam_button(callback: CallbackQuery):
    await FSMSpamUsers.message.set()
    await callback.message.answer(text('Наберите текст рассылки 👇⌨'),
                                  parse_mode=ParseMode.MARKDOWN,
                                  reply_markup=input_values_markup)
    await callback.answer()


@dp.message_handler(state=FSMSpamUsers.message)
async def process_spam_message(message: types.Message, state: FSMContext):
    # get all users
    for _ in get_all_users_stats():
        if message.from_user.id != _['ID пользователя']:
            await dp.bot.send_message(chat_id=_['ID пользователя'], text=message.text)
    await message.answer(text('Рассылка выполнена ✅'),
                         parse_mode=ParseMode.MARKDOWN,
                         reply_markup=authed_markup)
    await state.finish()
    await state.reset_state()


@dp.callback_query_handler(text='return', state="*")
@dp.callback_query_handler(text='cancel_admin', state="*")
async def process_cancel_button(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text('Выберите Ваши дальнейшие действия с помощью кнопок снизу 👇'),
                                  parse_mode=ParseMode.MARKDOWN,
                                  reply_markup=authed_markup)
    await callback.answer()
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await state.reset_state()


@dp.callback_query_handler(text='exit_admin')
async def process_start_command(callback: CallbackQuery):
    await callback.message.answer(text('Я могу посчитать стоимость авто 🚘 из Германии "под ключ" в РФ.',
                                       f'\n\nДля расчета нужна {(italic("ссылка"))} на конкретный авто.',
                                       f'\n\nЧто бы начать, нажмите кнопку ниже 👇'),
                                  reply_markup=start_markup,
                                  parse_mode=ParseMode.MARKDOWN)
    await callback.answer()


def register_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(process_moderate_command, commands=['moderate'], state=None)
    dp.register_message_handler(process_password_input, state=FSMLogin.password)
    dp.register_callback_query_handler(process_change_password_button, state=None)
    dp.register_message_handler(process_password_input, state=FSMChangePassword.password)
    dp.register_callback_query_handler(process_change_params_button, state=None)
    dp.register_callback_query_handler(process_change_exchange_div_button, state=FSMChangeParams.param)
    dp.register_callback_query_handler(process_change_change_dop_button, state=FSMChangeParams.param)
    dp.register_message_handler(process_param_value, state=FSMChangeParams.value)
    dp.register_callback_query_handler(process_spam_button, state=None)
    dp.register_message_handler(process_spam_message, state=FSMSpamUsers.message)
    dp.register_callback_query_handler(process_cancel_button, state="*")
