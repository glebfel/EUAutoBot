import datetime

from databases.db_models import SessionLocal, AuthedUsers


def check_user(user_id: int) -> bool:
    with SessionLocal() as session:
        user = session.query(AuthedUsers).filter(AuthedUsers.user_id == user_id).first()
        if user:
            return True
        return False


def add_user(user_id: int):
    with SessionLocal() as session:
        user = AuthedUsers(
            user_id=user_id,
            last_auth_date=datetime.date.today()
        )
        session.add(user)
        session.commit()


def update_user_last_auth(user_id: int):
    with SessionLocal() as session:
        session.query(AuthedUsers).filter_by(user_id=user_id).update({"last_auth_date": datetime.date.today()})
        session.commit()
