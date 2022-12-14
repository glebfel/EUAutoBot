import datetime
from typing import Optional

from sqlalchemy import func

from databases.db_models import SessionLocal, UserStats


def add_user(user_id: int):
    with SessionLocal() as session:
        param = UserStats(
            user_id=user_id,
            last_usage_date=datetime.date.today()
        )
        session.add(param)
        session.commit()


def get_start_command_usage_count_by_user(user_id: int) -> int:
    with SessionLocal() as session:
        user = session.query(UserStats).filter_by(user_id=user_id).first()
        if user:
            return user.start_command_count


def get_car_calculation_count_by_user(user_id: int) -> Optional[int]:
    with SessionLocal() as session:
        user = session.query(UserStats).filter_by(user_id=user_id).first()
        if user:
            return user.car_calculation_count
        return None


def get_feedback_usage_count_by_user(user_id: int) -> int:
    with SessionLocal() as session:
        user = session.query(UserStats).filter_by(user_id=user_id).first()
        return user.feedback_usage_count


def update_start_command_count(user_id: int):
    current_count = get_start_command_usage_count_by_user(user_id)
    if not current_count:
        add_user(user_id)
        return
    with SessionLocal() as session:
        session.query(UserStats).filter_by(user_id=user_id).update({"start_command_count": current_count + 1,
                                                                    "last_usage_date": datetime.date.today()})
        session.commit()


def update_car_calculation_count(user_id: int):
    current_count = get_car_calculation_count_by_user(user_id)
    if not current_count:
        current_count = 0
    with SessionLocal() as session:
        session.query(UserStats).filter_by(user_id=user_id).update({"car_calculation_count": current_count + 1,
                                                                    "last_usage_date": datetime.date.today()})
        session.commit()


def update_feedback_usage_count(user_id: int):
    current_count = get_feedback_usage_count_by_user(user_id)
    with SessionLocal() as session:
        session.query(UserStats).filter_by(user_id=user_id).update({"feedback_usage_count": current_count + 1,
                                                                    "last_usage_date": datetime.date.today()})
        session.commit()


def get_number_of_unique_users(from_timespan: datetime.date = None) -> int:
    with SessionLocal() as session:
        if from_timespan:
            users = session.query(UserStats).filter(UserStats.last_usage_date >= from_timespan).all()
        else:
            users = session.query(UserStats).all()
        return len(users)


def get_start_command_usage_overall() -> int:
    with SessionLocal() as session:
        count = session.query(func.sum(UserStats.start_command_count)).first()
        return count[0]


def get_car_calculation_count_overall() -> int:
    with SessionLocal() as session:
        count = session.query(
            func.sum(UserStats.car_calculation_count)).first()
        return count[0]


def get_feedback_usage_count_overall() -> int:
    with SessionLocal() as session:
        count = session.query(func.sum(UserStats.feedback_usage_count)).first()
        return count[0]


def get_all_users_stats() -> list[dict]:
    with SessionLocal() as session:
        users = session.query(UserStats).all()
    # convert to list of dicts
    users_list = []
    for _ in users:
        users_list.append({'ID ????????????????????????': _.user_id,
                           '???????????????????? ?????????????????????????? ????????': _.start_command_count,
                           '???????????????????? ???????????????? ???? ???????????????????? ?????????????? ?????????????????? ????????': _.car_calculation_count,
                           '???????????????????? ???????????????? ???? ?????????????????? ???????????????? ?????????? (????????????)': _.feedback_usage_count,
                           '???????? ???????????????????? ??????????????????????????': _.last_usage_date})
    return users_list
