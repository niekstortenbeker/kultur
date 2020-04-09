import arrow
import pytest
from data.dbsession import DbSession
from data.show import Show
from tests import fake_data
from update.data import all_theaters, replace_records
from update.theaters.theaterbremen import TheaterBremen


def test_all(database_light, theaters):
    # GIVEN an initialized filled database and updated theaters
    # WHEN all records are replaced
    added = replace_records(theaters)
    # THEN database has only new records
    session = DbSession.factory()
    result = session.query(Show).count()
    session.commit()
    assert added == result


def test_one_theater_(database_light, theater_bremen):
    # GIVEN an initialized filled database and one updated theater
    # WHEN this one theater is replaced
    added = replace_records(theater_bremen)
    # THEN database should only have the newly added records for this theater
    session = DbSession.factory()
    result = session.query(Show).filter_by(location=theater_bremen.name).count()
    session.commit()
    assert added == result


def test_one_theater(database_light, theater_bremen):
    # GIVEN an initialized filled database and one updated theater
    session = DbSession.factory()
    before_all = session.query(Show).count()
    before_theater_bremen = (
        session.query(Show).filter_by(location=theater_bremen.name).count()
    )
    # WHEN this one theater is replaced
    added = replace_records(theater_bremen)
    # THEN database should have only these records replaced
    all_records = session.query(Show).count()
    session.commit()
    assert all_records == before_all - before_theater_bremen + added


# noinspection PyTypeChecker
def test_raises_str():
    """replace_records() only accepts TheaterBase or list of TheaterBase"""
    with pytest.raises(TypeError):
        replace_records("these are not theaters")


# noinspection PyTypeChecker
def test_raises_str_list():
    """replace_records() only accepts TheaterBase or list of TheaterBase"""
    with pytest.raises(TypeError):
        replace_records(["these are not theaters"])


@pytest.fixture()
def theaters():
    theaters = all_theaters.copy()
    for theater in theaters:
        theater.program = fake_data.light_program(theater.name)
    return theaters


@pytest.fixture()
def theater_bremen():
    theater_bremen = TheaterBremen()
    theater_bremen.program = [
        Show(
            date_time=arrow.now(),
            title="bla",
            location=theater_bremen.name,
            category="stage",
        )
    ]
    return theater_bremen
