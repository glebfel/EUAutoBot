import json
import aiohttp
from models import Car, Customs

BASE_URL = "https://calcus.ru/rastamozhka-auto"

BASIC_HEADER = {"Accept": "*/*",
                "referer": "https://calcus.ru/rastamozhka-auto",
                "User-Agent": "Mozilla/5.0 (compatible; MSIE 10.0; Macintosh; Intel Mac OS X 10_7_3; Trident/6.0)"}


async def calculate_customs(car: Car) -> Customs:
    # fill form data
    form_data = {
        "calculate": 1,
        "owner": car.owner,
        "age": car.age,
        "engine": car.engine,
        "power": car.power,
        "power_unit": car.power_unit,
        "value": car.value,
        "price": car.price,
        "currency": "eur",
    }

    # get calculations
    session = aiohttp.ClientSession(headers=BASIC_HEADER)
    async with session.post(BASE_URL, data=form_data) as resp:
        calc_data = json.loads((await resp.text()))
        await session.close()

    # clean data
    for i in calc_data:
        if i not in ['tax_k', 'util_k', 'increase_counter']:
            calc_data[i] = calc_data[i].replace(',', '.').replace(' ', '')

    return Customs.parse_obj(calc_data)
