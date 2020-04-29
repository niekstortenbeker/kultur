import pytest
from kultur.data.dbsession import UninitializedDatabaseError
from kultur.view import data


def test_get_program_today(database_full):
    # GIVEN an initialized filled database
    # WHEN get_program_today() is ran
    result = data.get_program_today()
    # THEN I should get some shows
    assert len(result) > 1


def test_get_program_today_days(database_full):
    # GIVEN an initialized filled database
    # WHEN get_program_today() is ran
    result = data.get_program_today()
    # THEN all shows should be on the same day
    dates = set()
    for show in result:
        dates.add(show.date_time.day)

    assert len(dates) == 1


def test_get_program_week(database_full):
    # GIVEN an initialized filled database
    # WHEN get_program_today() is ran
    result = data.get_program_week()
    # THEN I should get some shows
    assert len(result) > 1


def test_get_program_week_days(database_full):
    # GIVEN an initialized filled database
    # WHEN get_program_week() is ran
    result = data.get_program_week()
    # THEN I should get shows for seven days
    dates = set()
    for show in result:
        dates.add(show.date_time.day)

    assert len(dates) == 7


def test_get_program_range_raises():
    """get_program_today() only works with a database connection"""
    with pytest.raises(UninitializedDatabaseError):
        data.get_program_today()
