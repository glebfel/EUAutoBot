from pathlib import Path
from os.path import exists

from core import settings
from databases import create_database, add_password, add_param

DB_NAME = 'bot.db'
DB_PATH = str(Path(__file__).parent) + '/' + DB_NAME


def start_database():
    create_database()
    if not exists(DB_PATH):
        add_password(settings.BOT_ADMIN_PASSWORD)
        add_param('exchange_div', 12)
        add_param('dop', 50000)
