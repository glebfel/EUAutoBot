from databases.db_models import SessionLocal, Params


def update_param(param: str, value: float):
    with SessionLocal() as session:
        session.query(Params).filter_by(param_name=param).update({"value": value})
        session.commit()


def add_param(param: str, value: float):
    with SessionLocal() as session:
        param = Params(
            param_name=param,
            value=value
        )
        session.add(param)
        session.commit()


def get_param_value(param: str) -> float:
    with SessionLocal() as session:
        param = session.query(Params).filter_by(param_name=param).first()
        return param.value
