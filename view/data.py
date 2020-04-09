from typing import List
import arrow
from data.dbsession import DbSession
from data.show import Show


def get_program_today() -> List[Show]:
    return get_program_range(1)


def get_program_week() -> List[Show]:
    return get_program_range(7)


def get_program_range(number_of_days: int) -> List[Show]:
    session = DbSession.factory()
    start = arrow.now("Europe/Berlin")
    stop = start.shift(days=+number_of_days).replace(
        hour=0, minute=0, second=0, microsecond=0, tzinfo="Europe/Berlin"
    )
    results = query_program_range(session, start, stop)
    return results


def query_program_range(session, start, end) -> List[Show]:
    results = (
        session.query(Show)
        .filter_by(dubbed=False)
        .filter(Show.date_time.between(start, end))
        .order_by(Show.date_time)
        .all()
    )
    return results
