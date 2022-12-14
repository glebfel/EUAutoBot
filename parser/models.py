from pydantic import BaseModel, Field
from typing import Optional

Rubbles = int
Euros = int
Kilometers = int

engine_types = {
    1: "Бензин",
    2: "Дизель",
    3: "Гибрид",
    4: "Электро",
    5: "Природный газ"
}


class Car(BaseModel):
    name: str
    owner: int = Field(ge=1, le=2, description="form of business: 1 - физ. лицо; 2 - юр. лицо;", default=1)
    age: str = Field(default="Новая")
    age_formatted: str = Field(default="0-3")
    engine: int = Field(ge=1, le=5, description="type of engine: 1 - gasoline; 2 - diesel; 3 - hybrid; 4 - electric; "
                                                "5 - natural gas")
    power_unit: int = Field(ge=1, le=2, description="engine power units: 1 - Hp; 2 - kW", default=1)
    power: int = Field(ge=0, description="engine power value")
    value: Optional[int] = Field(ge=0, description="engine capacity (in cubic centimeters)")
    mileage: Kilometers = Field(ge=0, default=0)
    damaged: bool = Field(description="if car was ever damaged or not", default=False)
    price_eu: Optional[Euros]
    price_ru: Optional[Rubbles]
    price_with_vat_eu: Euros
    price_with_vat_ru: Rubbles
    vat: int = Field(description="VAT tax value", default=19)


class Customs(BaseModel):
    sbor: Rubbles = Field(ge=0, description="Сбор")
    tax: Rubbles = Field(ge=0, description="Таможенная пошлина")
    tax_k: str
    util: Rubbles = Field(ge=0, description="Утилизационный сбор")
    util_k: str
    dop: int = Field(ge=0, description="Стоимость оформления СБКТС и ЭПТС")
    exchange_div: int = Field(ge=0, description="Процент разницы курса ЦБ и обменников")
    total: Rubbles = Field(ge=0, description="Итого")
