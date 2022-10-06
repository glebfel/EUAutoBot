# parse https://www.mobile.de/h

import pathlib
import sys
from datetime import datetime
import re

import validators
import exceptions
from core import custom_logger
from parser.models import Car
from bs4 import BeautifulSoup
from arsenic import services, browsers, get_session
from parser.get_exchange_rate import get_real_eu_rate
from pydantic import ValidationError

# Корень проекта
DIR_PATH = str(pathlib.Path(__file__).parent)

if sys.platform.startswith('win'):
    GECKODRIVER = DIR_PATH + '/geckodriver.exe'
else:
    GECKODRIVER = DIR_PATH + '/geckodriver'

custom_logger.info(GECKODRIVER)

BASIC_HEADER = {"Accept": "application/json",
                "referer": "https://www.mobile.de/",
                "User-Agent": "Mozilla/5.0 (compatible; MSIE 10.0; Macintosh; Intel Mac OS X 10_7_3; Trident/6.0)"}


def _validate_link(url: str):
    """
    Basic link validation
    :param url: url of the car from https://www.mobile.de/
    """
    # basic url validation
    if validators.url(url):
        # validate if url contains is mobel.de
        if 'mobile.de' in url:
            return
        else:
            raise exceptions.AnotherUrlError(url)
    else:
        raise exceptions.NotUrlError(url)


def _validate_age(age: str) -> str:
    """validate and convert age from value into range (https://calcus.ru/ format)"""
    age_v = datetime(day=1, month=int(age.strip().split('/')[0]), year=int(age.strip().split("/")[1]))
    years = (datetime.now() - age_v).days / 365
    if years < 3:
        return '0-3'
    if 3 <= years < 5:
        return '3-5'
    if 5 <= years < 7:
        return '5-7'
    if years >= 7:
        return '7-0'


def _validate_engine(engine: str) -> int:
    """validate engine type (https://calcus.ru/ format)"""

    if re.split(', | \\(', engine.strip())[0] in ['Бензиновый', 'Benzin', 'Petrol']:
        return 1
    if re.split(', | \\(', engine.strip())[0] in ['Дизельный', 'Diesel']:
        return 2
    if re.split(', | \\(', engine.strip())[0] in ['Гибридный', 'Hybrid']:
        return 3
    if re.split(', | \\(', engine.strip())[0] in ['Электрический', 'Electric', 'Elektro']:
        return 4


def _validate_digit_value(digit_value: str) -> str:
    """validate digit values (https://calcus.ru/ format)"""
    val = ''
    for _ in digit_value.strip().replace('.', '').replace(' ', ''):
        if _.isdigit() and _ != '³':
            val += _
    return val


async def get_car_data(url: str) -> Car:
    try:
        """Get info about the car by link (in https://calcus.ru/ format)"""
        # validate link
        _validate_link(url)

        # get page
        service = services.Geckodriver(binary=GECKODRIVER)
        browser = browsers.Firefox(**{'moz:firefoxOptions': {'args': ['-headless']}})
        async with get_session(service, browser) as session:
            await session.get(url)
            await session.wait_for_element(15, "li")
            page = await session.get_page_source()

        # parse page
        page = BeautifulSoup(page, 'lxml')
        car = {}
        # parse car name
        name = page.find(class_='listing-title u-margin-bottom-18')
        # ger/eng version of the site
        if name:
            car['name'] = name.h1.text + ' ' + name.div.text
        else:
            # for rus version of the site
            car['name'] = page.find(class_='h2 g-col-8').text

        # parse stats
        # for ger/eng version
        stats = page.find(class_='cBox cBox--content')
        if stats:
            stats = page.find(class_='cBox cBox--content').div
            stats = list(stats.children)
        else:
            # for rus version
            stats = []
            stats.extend(page.find(class_='attributes-box g-col-12'))
            stats.extend(page.find(class_='further-tec-data g-col-12'))

        for i in stats:
            # parse first registration
            if any(x in i.text for x in ['Первая регистрация', 'Erstzulassung', 'First Registration']):
                if not car.get('age'):
                    car['age'] = list(i.children)[1].text.strip()
                    car['age_formatted'] = _validate_age(list(i.children)[1].text)
            # parse engine type
            if any(x in i.text for x in ['Топливо', 'Kraftstoffart', 'Fuel']):
                if not car.get('engine'):
                    car['engine'] = _validate_engine(list(i.children)[1].text)
            # parse engine power
            if any(x in i.text for x in ['Мощность', 'Leistung', 'Power']):
                if not car.get('power'):
                    car['power'] = list(i.children)[1].text.split()[2].replace("(", " ")
            # parse engine capacity
            if any(x in i.text for x in ['Объем двигателя', 'Hubraum', 'Cubic Capacity']):
                if not car.get('value'):
                    car['value'] = _validate_digit_value(list(i.children)[1].text)
            # parse mileage
            if any(x in i.text for x in ['Пробег', 'Kilometerstand', 'Mileage']):
                if not car.get('mileage'):
                    car['mileage'] = _validate_digit_value(list(i.children)[1].text)
            # parse damages
            if any(x in i.text for x in ['Состояние транспортного средства', 'Fahrzeugzustand', 'Vehicle condition']):
                if any(x in i.text for x in ['Не попадало в ДТП', 'Unfallfrei', 'Accident-free']):
                    car['damaged'] = False
                else:
                    car['damaged'] = True

        # parse price
        price = page.find(class_='price-and-financing-row')

        # ger/eng version of the site
        if price:
            # check for sales
            sales = page.find(class_='h3 u-text-red u-own-line-through-red')
            if sales:
                car['price_with_vat_eu'] = _validate_digit_value(
                    page.find(class_='price-and-financing-row').text.split('€')[1])
            else:
                num_of_prices = len(page.find(class_='price-and-financing-row').text.split('€'))
                if num_of_prices > 2:
                    car['price_with_vat_eu'] = _validate_digit_value(
                        page.find(class_='price-and-financing-row').text.split('€')[0])
                    car['price_eu'] = _validate_digit_value(page.find(class_='price-and-financing-row').text.split('€')[1])
                    # calculate without vat price in rubles
                    car['price_ru'] = round(int(car['price_eu']) * await get_real_eu_rate())
                else:
                    car['price_with_vat_eu'] = _validate_digit_value(
                        page.find(class_='price-and-financing-row').text.split('€')[0])

        # for rus version of the site
        else:
            num_of_prices = len(page.find(class_='header-price-box g-col-4').text.split('€'))
            if num_of_prices > 2:
                car['price_with_vat_eu'] = _validate_digit_value(
                    page.find(class_='header-price-box g-col-4').text.split('€')[0])
                car['price_eu'] = _validate_digit_value(page.find(class_='header-price-box g-col-4').text.split('€')[1])
                # calculate without vat price in rubles
                car['price_ru'] = round(int(car['price_eu']) * await get_real_eu_rate())
            else:
                car['price_with_vat_eu'] = _validate_digit_value(
                    page.find(class_='header-price-box g-col-4').text.split('€')[0])

        # calculate price in rubles
        car['price_with_vat_ru'] = round(int(car['price_with_vat_eu']) * await get_real_eu_rate())

        return Car.parse_obj(car)
    except ValidationError:
        if 'damaged' not in car:
            car['damaged'] = False
            return Car.parse_obj(car)
        raise exceptions.CarAttributeEmptyError()


