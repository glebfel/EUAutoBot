from pydantic import BaseSettings


class Settings(BaseSettings):
    API_KEY: str

    class Config:
        env_file = ".env"


settings = Settings(_env_file="config.env")
