import datetime
from os.path import exists
from pathlib import Path

from core import custom_logger, settings
from sqlalchemy import Column, String, Integer, DATE, create_engine, LargeBinary
from sqlalchemy.orm import declarative_base, sessionmaker

from databases import add_password, add_param

DB_NAME = 'bot.db'
DB_PATH = str(Path(__file__).parent) + '/' + DB_NAME

# create db object
Base = declarative_base()
engine = create_engine(f"sqlite:///{DB_PATH}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class IdMixin(object):
    id = Column(Integer, primary_key=True, autoincrement=True)


class Password(Base, IdMixin):
    __tablename__ = 'password'
    pw_hash = Column(LargeBinary, unique=True, nullable=False)
    salt = Column(LargeBinary, unique=True, nullable=False)
    last_update_date = Column(DATE, default=datetime.date.today())


class AuthedUsers(Base, IdMixin):
    __tablename__ = 'authed_users'
    user_id = Column(Integer, unique=True, nullable=False)
    last_auth_date = Column(DATE, default=datetime.date.today())


class Params(Base, IdMixin):
    __tablename__ = 'params'
    param_name = Column(String, unique=True, nullable=False)
    value = Column(Integer, nullable=False)


class UserStats(Base, IdMixin):
    __tablename__ = 'user_stats'
    user_id = Column(Integer, unique=True, nullable=False)
    start_command_count = Column(Integer, default=1)
    car_calculation_count = Column(Integer, default=0)
    feedback_usage_count = Column(Integer, default=0)
    last_usage_date = Column(DATE, default=datetime.date.today())


def start_database():
    if not exists(DB_PATH):
        Base.metadata.create_all(bind=engine)
        add_password(settings.BOT_ADMIN_PASSWORD)
        add_param('exchange_div', 12)
        add_param('dop', 50000)
    custom_logger.info('DB was successfully initialized!')
