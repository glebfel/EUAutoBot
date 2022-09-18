from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ParseMode, CallbackQuery
from aiogram.utils.markdown import text

from telegram_bot.keyboards import login_markup, authed_markup, change_params_markup, input_values_markup
from telegram_bot.init_bot import dp
from databases import get_password, update_password, update_param


class FSMLogin(StatesGroup):
    password = State()


class FSMChangePassword(StatesGroup):
    password = State()


class FSMChangeParams(StatesGroup):
    param = State()
    value = State()


@dp.message_handler(commands=['moderate'], state=None)
async def process_moderate_command(message: types.Message):
    await FSMLogin.password.set()
    await message.answer(text('Приветствую Вас 👋',
                              f'Вы зашли в режим модератора 📝',
                              f'\nЧтобы продолжить наберите пароль 🗝 для доступа к админ-панели',
                              sep="\n"),
                         parse_mode=ParseMode.MARKDOWN,
                         reply_markup=login_markup)


@dp.message_handler(state=FSMLogin.password)
async def process_password_input(message: types.Message, state: FSMContext):
    if message.text == get_password():
        await message.answer(text('Вы успешно авторизованы 🚪',
                                  'Выберите Ваши дальнейшие действия с помощью кнопок снизу 👇',
                                  sep="\n\n"),
                             parse_mode=ParseMode.MARKDOWN,
                             reply_markup=authed_markup)
        await state.finish()
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
    await state.finish()


@dp.callback_query_handler(text='change_params', state=None)
async def process_change_params_button(callback: CallbackQuery):
    await FSMChangeParams.param.set()
    await callback.message.answer(text('Выберите параметр, значение которого хотели бы изменить, с помощью кнопок '
                                       'ниже 👇'),
                                  parse_mode=ParseMode.MARKDOWN,
                                  reply_markup=change_params_markup)
    await callback.answer()


@dp.callback_query_handler(text='change_currency_div', state=FSMChangeParams.param)
async def process_change_currency_div_button(callback: CallbackQuery, state=FSMContext):
    await callback.message.answer(text('Введите число 👇⌨',
                                       '(доли вводить через точку, например: 23.4)',
                                       sep="\n"),
                                  parse_mode=ParseMode.MARKDOWN,
                                  reply_markup=input_values_markup)
    await callback.answer()
    async with state.proxy() as data:
        data['param'] = 'currency_div'
    await FSMChangeParams.next()


@dp.callback_query_handler(text='change_dop', state=FSMChangeParams.param)
async def process_change_change_dop_button(callback: CallbackQuery, state=FSMContext):
    await callback.message.answer(text('Введите число 👇⌨ (доли вводить через точку, например: 23.4)'),
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
            value = float(message.text)
            update_param(data['param'], value)
            await message.answer(text('Значение сохранено ✅'),
                                 parse_mode=ParseMode.MARKDOWN,
                                 reply_markup=authed_markup)
        await state.finish()
    except (TypeError, ValueError):
        await message.answer(text('🛑 Вы ввели некорректное значение 🛑',
                                  'Требуется ввести число (доли вводить через точку, например: 23.4)',
                                  'Повторите попытку 🔄',
                                  sep="\n"),
                             parse_mode=ParseMode.MARKDOWN,
                             reply_markup=input_values_markup)


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


@dp.callback_query_handler(text='exit_admin', state="*")
async def process_exit_button(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text("Выполните команду /start чтобы вернуться к началу 🔙"))
    await callback.answer()
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()


def register_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(process_moderate_command, commands=['moderate'], state=None)
    dp.register_message_handler(process_password_input, state=FSMLogin.password)
    dp.callback_query_handler(process_change_password_button, state=None)
    dp.register_message_handler(process_password_input, state=FSMChangePassword.password)
    dp.callback_query_handler(process_change_params_button, state=None)
    dp.callback_query_handler(process_change_currency_div_button, state=FSMChangeParams.param)
    dp.callback_query_handler(process_change_change_dop_button, state=FSMChangeParams.param)
    dp.message_handler(process_param_value, state=FSMChangeParams.value)
    dp.register_callback_query_handler(process_cancel_button, state="*")
    dp.register_callback_query_handler(process_exit_button, state="*")
