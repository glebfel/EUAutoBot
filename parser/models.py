from pydantic import BaseModel, Field

Rubbles = float
Euros = int
Kilometers = int


class Car(BaseModel):
    name: str
    owner: int = Field(ge=1, le=2, description="form of business: 1 - физ. лицо; 2 - юр. лицо;", default=1)
    age: str
    engine: int = Field(ge=1, le=4, description="type of engine: 1 - gasoline; 2 - diesel; 3 - hybrid; 4 - electric")
    power_unit: int = Field(ge=1, le=2, description="engine power units: 1 - Hp; 2 - kW", default=1)
    power: int = Field(ge=0, description="engine power value")
    value: float = Field(ge=0, description="engine capacity (in cubic centimeters)")
    mileage: Kilometers = Field(ge=0)
    damaged: bool = Field(description="if car was ever damaged or not", default=False)
    price: Euros
    price_with_vat: Euros
    vat: int = Field(description="VAT tax value", default=19)


class Customs(BaseModel):
    sbor: Rubbles = Field(ge=0, description="Сбор")
    tax: Rubbles = Field(ge=0, description="Таможенная пошлина")
    tax_k: str
    util: Rubbles = Field(ge=0, description="Утилизационный сбор")
    util_k: str
    total: Rubbles = Field(ge=0, description="Итого")
