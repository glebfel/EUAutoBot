# parse https://www.mobile.de/

from datetime import datetime

import validators
import exceptions
from models import Car
from bs4 import BeautifulSoup
from arsenic import services, browsers, get_session

BASIC_HEADER = {"Accept": "application/json",
                "referer": "https://www.mobile.de/",
                "User-Agent": "Mozilla/5.0 (compatible; MSIE 10.0; Macintosh; Intel Mac OS X 10_7_3; Trident/6.0)"}


def _validate_link(url: str) -> bool:
    """
    Basic link validation
    :param url: url of the car from https://www.mobile.de/
    """
    # basic url validation
    if validators.url(url):
        # validate if url contains is mobel.de
        if 'mobile.de' in url:
            return True
    return False


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
    if engine.strip() in ['Бензиновый', 'Benzin', 'Petrol']:
        return 1
    if engine.strip() in ['Дизельный', 'Diesel']:
        return 2
    if engine.strip() in ['Гибридный', 'Hybrid']:
        return 3
    if engine.strip() in ['Электрический', 'Electric']:
        return 4


def _validate_digit_value(digit_value: str) -> str:
    """validate digit values (https://calcus.ru/ format)"""
    val = ''
    for _ in digit_value.strip().replace('.', '').replace(' ', ''):
        if _.isdigit() and _ != '³':
            val += _
    return val


async def get_car_data(url: str) -> Car:
    # validate link
    if not _validate_link(url):
        raise exceptions.InvalidUrlError(url)

    # get page
    service = services.Geckodriver()
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
            car['age'] = _validate_age(list(i.children)[1].text)
        # parse engine type
        if any(x in i.text for x in ['Топливо', 'Kraftstoffart', 'Fuel']):
            car['engine'] = _validate_engine(list(i.children)[1].text)
        # parse engine power
        if any(x in i.text for x in ['Мощность', 'Leistung', 'Power']):
            car['power'] = list(i.children)[1].text.split()[2].replace("(", " ")
        # parse engine capacity
        if any(x in i.text for x in ['Объем двигателя', 'Hubraum', 'Cubic Capacity']):
            car['value'] = _validate_digit_value(list(i.children)[1].text)
        # parse mileage
        if any(x in i.text for x in ['Пробег', 'Kilometerstand', 'Mileage']):
            car['mileage'] = _validate_digit_value(list(i.children)[1].text)
        # parse damages
        if any(x in i.text for x in ['Состояние транспортного средства', 'Fahrzeugzustand', 'Vehicle condition']):
            if any(x in i.text.split()[1] for x in ['Не попадало в ДТП', 'Unfallfrei', 'Accident-free']):
                car['damaged'] = False
            else:
                car['damaged'] = True

    # parse price
    price = page.find(class_='price-and-financing-row')
    # ger/eng version of the site
    if price:
        car['price'] = _validate_digit_value(page.find(class_='price-and-financing-row').text.split('€')[1])
        car['price_with_vat'] = _validate_digit_value(page.find(class_='price-and-financing-row').text.split('€')[0])
    else:
        # for rus version of the site
        car['price_with_vat'] = page.find(class_='header-price-box g-col-4').text
    return Car.parse_obj(car)