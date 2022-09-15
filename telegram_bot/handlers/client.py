from aiogram import types, Dispatcher
from aiogram.types import ParseMode, CallbackQuery
from aiogram.utils.markdown import text, italic, bold
from telegram_bot.init_bot import dp
from telegram_bot.inline_keyboard import start_markup


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.answer(text('Я могу посчитать стоимость авто 🚘 из Германии "под ключ" в РФ.',
                              f'\n\nДля расчета нужна {(italic("ссылка"))} на конкретный авто.',
                              f'\n\nЧто бы начать, нажмите кнопку ниже 👇'),
                         reply_markup=start_markup,
                         parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.answer(text(bold("Доступные команды:"),
                              "/start - возврат к началу ⏭",
                              "/moderate - режим модератора 🖥 (доступен только администратору бота)",
                              sep="\n"
                              ),
                         parse_mode=ParseMode.MARKDOWN)


@dp.callback_query_handler(text="calculate")
async def process_calculate_button(callback: CallbackQuery):
    await callback.message.answer("Пожалуйста, пришлите ссылку на интересуемое авто 🚙🔍")


@dp.message_handler()
async def process_other_commands(message: types.Message):
    await message.answer(text("Не могу распознать введенную команду 🧐❗",
                              "\nДля просмотра доступных команд воспользуйтесь /help 🧾"),
                         parse_mode=ParseMode.MARKDOWN)


def register_client_handlers(dp: Dispatcher):
    dp.register_message_handler(process_start_command)
    dp.register_message_handler(process_help_command)
    dp.register_message_handler(process_other_commands)
