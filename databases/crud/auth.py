import datetime

from databases.db_models import SessionLocal, Password


def update_password(password: str):
    current_password = get_password()
    with SessionLocal() as session:
        session.query(Password).filter_by(password=current_password).update({"password": password,
                                                                             "last_update_date": datetime.date.today()})
        session.commit()


def add_password(password: str):
    with SessionLocal() as session:
        password = Password(
            password=password,
            last_update_date=datetime.date.today()
        )
        session.add(password)
        session.commit()


def get_password() -> str:
    with SessionLocal() as session:
        password = session.query(Password).filter(Password.password is not None).first()
        return password.password
