import datetime

from aiogram import types, Dispatcher
from aiogram.types import ParseMode, CallbackQuery
from aiogram.utils.markdown import text, italic, bold
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from loguru import logger

from telegram_bot.init_bot import dp
from telegram_bot.keyboards import start_markup, error_markup, car_info_markup, get_phone_markup, car_error_markup
from parser import get_car_data, calculate_customs, Car, Customs, engine_types
from exceptions import AnotherUrlError, NotUrlError, CarAttributeEmptyError
from parser import get_cbr_eu_rate
from databases import update_start_command_count, update_car_calculation_count, update_feedback_usage_count


class FSM(StatesGroup):
    link = State()


async def format_bot_output(car: Car, customs: Customs) -> str:
    if car.price_eu:
        output_text = text(str(bold(car.name.replace("*", "")).replace("\\", "")),
                           f"\n{bold('Двигатель:')} {engine_types.get(car.engine)}, {car.value} см³, {car.power} л.с.",
                           f"{bold('Дата постановки на учет:')} {car.age}",
                           f"{bold('Пробег:')} {car.mileage} км",
                           f"{'🛑 Была в ДТП' if car.damaged else '✅ Не попадала в ДТП'}\n",
                           f"{bold('Стоимость авто: 💸')}",
                           f"В Евро: €{car.price_eu:,} без НДС (€{car.price_with_vat_eu:,} с {car.vat}% НДС) НДС=€{car.price_with_vat_eu - car.price_eu:,}",
                           f"В Рублях: ₽{car.price_ru:,} без НДС (₽{car.price_with_vat_ru:,} с {car.vat}% НДС) НДС=₽{car.price_with_vat_ru - car.price_ru:,}",
                           f"\n{bold('Таможенное оформление в РФ:')}",
                           f"{bold('Таможенный сбор:')} ₽{customs.sbor:,}",
                           f"{bold('Пошлина:')} ₽{customs.tax:,}",
                           f"{bold('Утилизационный сбор:')} ₽{customs.util:,}\n",
                           f"{bold('Оформление СБКТС и ЭПТС:')} ~ ₽{customs.dop:,}\n",
                           bold(f'Итого: ₽{car.price_ru + customs.total:,} 🚙\n'),
                           f"Дата проведения расчета: {datetime.datetime.today().date()}, курс ЦБ 1€ = {await get_cbr_eu_rate()}₽",
                           str(italic(
                               f"*расчет стоимости произведен с учетом курса ЦБ на день запроса +{customs.exchange_div}% (курс обменников). "
                               "В расчет не включена стоимость доставки авто, услуг возврата НДС, услуг брокеров и др. "
                               "возможных дополнительных платежей.")).replace("\\", ""),
                           sep="\n")
    else:
        output_text = text(
            f"❗{bold('Машина продается без возможности возврата НДС')}❗",
            str(italic(
                "*Такая покупка не всегда выгодна. "
                "Рекомендуем искать автомобиль с возможностью возврата НДС. Как правило продавцы таких "
                "автомобилей - автосалоны.\n")).replace("\\", ""),
            str(bold(car.name.replace("*", "")).replace("\\", "")),
            f"\n{bold('Двигатель:')} {engine_types.get(car.engine)}, {car.value} см³, {car.power} л.с.",
            f"{bold('Дата постановки на учет:')} {car.age}",
            f"{bold('Пробег:')} {car.mileage} км",
            f"{'🛑 Была в ДТП' if car.damaged else '✅ Не попадала в ДТП'}\n",
            f"{bold('Стоимость авто: 💸')}",
            f"В Евро: €{car.price_with_vat_eu:,}",
            f"В Рублях: ₽{car.price_with_vat_ru:,}",
            f"\n{bold('Таможенное оформление в РФ:')}",
            f"{bold('Таможенный сбор:')} ₽{customs.sbor:,}",
            f"{bold('Пошлина:')} ₽{customs.tax:,}",
            f"{bold('Утилизационный сбор:')} ₽{customs.util:,}\n",
            f"{bold('Оформление СБКТС и ЭПТС:')} ~ ₽{customs.dop:,}\n",
            bold(f'Итого: ₽{car.price_with_vat_ru + customs.total:,} 🚙\n'),
            f"Дата проведения расчета: {datetime.datetime.today().date()}, курс ЦБ 1€ = {await get_cbr_eu_rate()}₽",
            str(italic(
                f"*расчет стоимости произведен с учетом курса ЦБ на день запроса +{customs.exchange_div}% (курс обменников). "
                "В расчет не включена стоимость доставки авто, услуг возврата НДС, услуг брокеров и др. "
                "возможных дополнительных платежей.")).replace("\\", ""),
            sep="\n")
    return output_text


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.answer(text('Я могу посчитать стоимость авто 🚘 из Германии "под ключ" в РФ.',
                              f'\n\nДля расчета нужна {(italic("ссылка"))} на конкретный авто.',
                              f'\n\nЧто бы начать, нажмите кнопку ниже 👇'),
                         reply_markup=start_markup,
                         parse_mode=ParseMode.MARKDOWN)
    update_start_command_count(message.from_user.id)


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.answer(text(bold("Доступные команды:"),
                              "/start - возврат к началу ⬆",
                              "/moderate - режим модератора 🖥 (доступен только администратору бота)",
                              sep="\n"
                              ),
                         parse_mode=ParseMode.MARKDOWN)


@dp.callback_query_handler(text='another', state=None)
@dp.callback_query_handler(text='retry', state=None)
@dp.callback_query_handler(text='calculate', state=None)
async def process_calculate_button(callback: CallbackQuery):
    await FSM.link.set()
    await callback.message.answer("Пожалуйста, пришлите ссылку на интересуемое авто 🚙🔍")
    await callback.answer()
    update_car_calculation_count(callback.from_user.id)


@dp.message_handler(state=FSM.link)
async def process_link_input(message: types.Message, state: FSMContext):
    try:
        await message.answer(text('Выполняю запрос ⏳'))

        logger.info(f'Processing "{message.text}" request ...')
        # get info about the car from https://www.mobile.de/
        car = await get_car_data(message.text)
        # calculate customs upon given car info
        customs = await calculate_customs(car)
        await message.answer(await format_bot_output(car, customs),
                             parse_mode=ParseMode.MARKDOWN,
                             reply_markup=car_info_markup)
    except NotUrlError as ex:
        logger.error(ex)
        await message.answer(text('Ой ... Кажется Вы передали не ссылку 🤨',
                                  'Для того чтобы правильно передать ссылку:',
                                  '◽ скопируйте её из адресной строки браузера 🌐',
                                  f'◽ воспользуйтесь кнопкой {(italic("поделиться"))} в приложении 📱',
                                  sep="\n\n"),
                             reply_markup=error_markup,
                             parse_mode=ParseMode.MARKDOWN)
    except AnotherUrlError as ex:
        logger.error(ex)
        await message.answer(text('Похоже Вы передали ссылку на другой сайт 🤔',
                                  'Для того чтобы правильно передать ссылку:',
                                  '◽ скопируйте её из адресной строки браузера 🌐',
                                  f'◽ воспользуйтесь кнопкой {(italic("поделиться"))} в приложении 📱',
                                  sep="\n\n"),
                             reply_markup=error_markup,
                             parse_mode=ParseMode.MARKDOWN)
    except AttributeError as ex:
        logger.error(ex)
        await message.answer(text('Похоже Вы передали ссылку на страницу сайта mobile.de не содержащую данных об авто '
                                  '🤔',
                                  'Для того чтобы правильно передать ссылку:',
                                  '◽ скопируйте её из адресной строки браузера 🌐',
                                  f'◽ воспользуйтесь кнопкой {(italic("поделиться"))} в приложении 📱',
                                  sep="\n\n"),
                             reply_markup=error_markup,
                             parse_mode=ParseMode.MARKDOWN)
    except CarAttributeEmptyError as ex:
        logger.error(type(ex))
        logger.error(ex)
        await message.answer(text(f'Похоже, что объявление которое Вы передали, не содержит параметра "{italic(ex)}" '
                                  f'нужного '
                                  f'для расчетов 🛑',
                                  'К сожалению, мы не можем рассчитать для него стоимость ... 😔',
                                  sep="\n\n"),
                             reply_markup=car_error_markup,
                             parse_mode=ParseMode.MARKDOWN)
    except Exception as ex:
        logger.error(type(ex))
        logger.error(ex)
        await message.answer(text("Что-то пошло не так ... 🥴",
                                  "Повторите попытку позже 😔",
                                  sep="\n\n"),
                             reply_markup=error_markup
                             )
    finally:
        await state.finish()


@dp.callback_query_handler(text='call')
async def process_call_button(callback: CallbackQuery):
    await callback.message.answer(text("+74993894054"), reply_markup=get_phone_markup)
    await callback.answer()
    update_feedback_usage_count(callback.from_user.id)


@dp.callback_query_handler(text='cancel', state="*")
async def process_cancel_button(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text("Благодарим Вас за использование нашего бота 😊",
                                       "Выполните команду /start чтобы вернуться к началу ⬆",
                                       sep="\n\n"))
    await callback.answer()
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()


def register_client_handlers(dp: Dispatcher):
    dp.register_message_handler(process_start_command, commands=['start'])
    dp.register_message_handler(process_help_command, commands=['help'])
    dp.register_callback_query_handler(process_calculate_button, state=None)
    dp.register_message_handler(process_link_input, state=FSM.link)
    dp.register_callback_query_handler(process_cancel_button, state="*")
