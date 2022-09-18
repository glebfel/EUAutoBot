from pathlib import Path

from sqlalchemy import Column, String, Integer, DATE, create_engine, FLOAT
from sqlalchemy.orm import declarative_base, sessionmaker

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
    password = Column(String, unique=True, nullable=False)
    last_update_date = Column(DATE, nullable=False)


class Params(Base, IdMixin):
    __tablename__ = 'params'
    param_name = Column(String, unique=True, nullable=False)
    value = Column(FLOAT, nullable=False)


def create_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
