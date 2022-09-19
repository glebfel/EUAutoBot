import pathlib
from pydantic import BaseSettings

# current directory
DIR_PATH = str(pathlib.Path(__file__).parent)


class Settings(BaseSettings):
    API_KEY: str

    class Config:
        env_file = ".env"


settings = Settings(_env_file=DIR_PATH + "/config.env")
