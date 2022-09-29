import pathlib
from pydantic import BaseSettings, Field
from dotenv import load_dotenv

# current directory
DIR_PATH = str(pathlib.Path(__file__).parent)


class Settings(BaseSettings):
    API_KEY: str = Field(..., env="API_KEY")
    BOT_ADMIN_PASSWORD = Field(..., env="BOT_ADMIN_PASSWORD")

    class Config:
        env_prefix = ""
        case_sentive = False
        env_file = '.env'
        env_file_encoding = 'utf-8'


# load variables from .env
load_dotenv(override=True)

# load vars to settings
settings = Settings()
