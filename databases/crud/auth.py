import datetime

from databases.passwords_handler import hash_new_password, is_correct_password
from databases.db_models import SessionLocal, Password


def update_password(password: str):
    salt, pw_hash = hash_new_password(password)
    with SessionLocal() as session:
        session.query(Password).filter(Password.pw_hash is not None).update({"pw_hash": pw_hash,
                                                                             "salt": salt,
                                                                             "last_update_date": datetime.date.today()})
        session.commit()


def add_password(password: str):
    with SessionLocal() as session:
        salt, pw_hash = hash_new_password(password)
        password = Password(
            pw_hash=pw_hash,
            salt=salt,
            last_update_date=datetime.date.today()
        )
        session.add(password)
        session.commit()


def check_password(password: str) -> bool:
    with SessionLocal() as session:
        pw_db = session.query(Password).filter(Password.pw_hash is not None).first()
        return is_correct_password(pw_db.pw_hash, password, pw_db.salt)
