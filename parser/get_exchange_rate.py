import json

import aiohttp
from databases import get_param_value

BASE_URL = "https://www.cbr-xml-daily.ru/daily_json.js"

BASIC_HEADER = {"Accept": "*/*",
                "User-Agent": "Mozilla/5.0 (compatible; MSIE 10.0; Macintosh; Intel Mac OS X 10_7_3; Trident/6.0)"}


async def get_cbr_eu_rate() -> float:
    """Get official CBR Euro/Ruble exchange rate"""
    # get CB official exchange rate
    session = aiohttp.ClientSession(headers=BASIC_HEADER)
    async with session.get(BASE_URL) as resp:
        rates = json.loads((await resp.text()))
        await session.close()
    return rates["Valute"]["EUR"]["Value"]


async def get_real_eu_rate() -> float:
    """Get current EUR/RUB currency exchange rate of """
    # get CBR official exchange rate
    off_rate = await get_cbr_eu_rate()
    # calculate real exchange rate
    real_rate = off_rate * (get_param_value('exchange_div') / 100 + 1)
    return real_rate
