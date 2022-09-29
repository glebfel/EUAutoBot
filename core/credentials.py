import pathlib
from pydantic import BaseSettings, Field
from dotenv import load_dotenv

# root directory
ROOT_PATH = str(pathlib.Path(__file__).parent.parent)


class Settings(BaseSettings):
    API_KEY: str = Field(..., env="API_KEY")
    BOT_ADMIN_PASSWORD: str = Field(..., env="BOT_ADMIN_PASSWORD")

    class Config:
        env_prefix = ""
        case_sentive = False
        env_file = '.env'
        env_file_encoding = 'utf-8'


# load variables from .env
load_dotenv(dotenv_path=ROOT_PATH + "/config.env")

# load vars to settings
settings = Settings()
