import pathlib
from pydantic import BaseSettings, Field

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


# load vars to settings
settings = Settings()
