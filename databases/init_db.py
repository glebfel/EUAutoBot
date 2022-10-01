from os.path import exists
from pathlib import Path

from core import custom_logger, settings
from databases import add_password, add_param
from databases.db_models import create_database

DB_NAME = 'bot.db'
DB_PATH = str(Path(__file__).parent) + '/' + DB_NAME


def start_database():
    if not exists(DB_PATH):
        create_database()
        add_password(settings.BOT_ADMIN_PASSWORD)
        add_param('exchange_div', 12)
        add_param('dop', 50000)
        custom_logger.info('DB was successfully created!')
    custom_logger.info('DB was successfully initialized!')
