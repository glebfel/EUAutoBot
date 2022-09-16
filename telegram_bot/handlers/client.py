from aiogram import types, Dispatcher
from aiogram.types import ParseMode, CallbackQuery
from aiogram.utils.markdown import text, italic, bold
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from telegram_bot.init_bot import dp
from telegram_bot.inline_keyboard import start_markup, error_markup
from parser import get_car_data, calculate_customs, Car, Customs, engine_types
from exceptions import AnotherUrlError, NotUrlError


class FSM(StatesGroup):
    link = State()


def format_bot_output(car: Car, customs: Customs) -> str:
    output_text = text(bold(car.name),
                       f"\n{bold('Двигатель:')} {engine_types.get(car.engine)}, {car.value} см³, {car.power} л.с.",
                       f"{bold('Год постановки на учет:')} {car.age}",
                       f"{bold('Пробег:')} {car.mileage}",
                       f"{'🛑 Была в ДТП' if car.damaged else '✅ Не попадала в ДТП'}\n",
                       f"{bold('Стоимость авто: 💸')}",
                       f"В Евро: €{car.price_eu:,} без НДС (€{car.price_with_vat_eu:,} с {car.vat}% НДС) НДС=€{car.price_with_vat_eu - car.price_eu:,}",
                       f"В Рублях: ₽{car.price_ru:,} без НДС (₽{car.price_with_vat_ru:,} с {car.vat}% НДС) НДС=₽{car.price_with_vat_ru - car.price_ru:,}",
                       f"\n{bold('Таможенное оформление в РФ:')}",
                       f"{bold('Таможенный сбор:')} ₽{customs.sbor:,}",
                       f"{bold('Пошлина:')} ₽{customs.tax:,}",
                       f"{bold('Утилизационный сбор:')} ₽{customs.util:,}\n",
                       f"{bold('Оформление СБКТС и ЭПТС:')} ~ ₽{customs.dop:,}\n",
                       bold(f'Итого: ₽{car.price_ru + customs.total:,} 🚙'),
                       sep="\n")
    return output_text


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
                              "/start - возврат к началу ⬆",
                              "/moderate - режим модератора 🖥 (доступен только администратору бота)",
                              sep="\n"
                              ),
                         parse_mode=ParseMode.MARKDOWN)


@dp.callback_query_handler(text='retry', state=None)
@dp.callback_query_handler(text='calculate', state=None)
async def process_calculate_button(callback: CallbackQuery):
    await FSM.link.set()
    await callback.message.answer("Пожалуйста, пришлите ссылку на интересуемое авто 🚙🔍")
    await callback.answer()


@dp.callback_query_handler(text='cancel', state="*")
async def process_cancel_button(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text("Благодарим Вас за использование нашего бота 😊",
                                       "Выполните команду /start чтобы вернуться к началу ⬆",
                                       sep="\n\n"))
    await callback.answer()
    await state.finish()


@dp.message_handler(state=FSM.link)
async def process_link_input(message: types.Message, state: FSMContext):
    try:
        await message.answer(text('Выполняется запрос ⏳'))
        # get info about the car from https://www.mobile.de/
        car = await get_car_data(message.text)
        # calculate customs upon given car info
        customs = await calculate_customs(car)
        await message.answer(format_bot_output(car, customs), parse_mode=ParseMode.MARKDOWN)
    except NotUrlError:
        await message.answer(text('Ой ... Кажется Вы передали не ссылку 🤨',
                                  'Для того чтобы правильно передать ссылку:',
                                  '◽ скопируйте её из адресной строки браузера 🌐',
                                  f'◽ воспользуйтесь кнопкой {(italic("поделиться"))} в приложении 📱',
                                  sep="\n\n"),
                             reply_markup=error_markup,
                             parse_mode=ParseMode.MARKDOWN)
    except AnotherUrlError:
        await message.answer(text('Похоже Вы передали ссылку на другой сайт 🤔',
                                  'Для того чтобы правильно передать ссылку:',
                                  '◽ скопируйте её из адресной строки браузера 🌐',
                                  f'◽ воспользуйтесь кнопкой {(italic("поделиться"))} в приложении 📱',
                                  sep="\n\n"),
                             reply_markup=error_markup,
                             parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        await message.answer(str(e))
        await message.answer(text("Что-то пошло не так ... 🥴",
                                  "Повторите попытку позже 😔",
                                  sep="\n\n"))
    finally:
        await state.finish()


@dp.message_handler()
async def process_other_commands(message: types.Message):
    await message.answer(text("Не могу распознать введенную команду 🧐❗",
                              "\nДля просмотра доступных команд воспользуйтесь /help 🧾"),
                         parse_mode=ParseMode.MARKDOWN)


def register_client_handlers(dp: Dispatcher):
    dp.register_message_handler(process_start_command)
    dp.register_message_handler(process_help_command)
    dp.register_callback_query_handler(process_calculate_button, state=None)
    dp.register_message_handler(process_link_input, state=FSM.link)
    dp.register_callback_query_handler(process_cancel_button, state="*")
    dp.register_message_handler(process_other_commands)
