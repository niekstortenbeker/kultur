import arrow
import pytest
from data.dbsession import DbSession
from data.show import Show


def test_add_minimal_show_empty_database(database_empty, minimal_show):
    # GIVEN an initialized empty database
    # WHEN a Show is added
    session = DbSession.factory()
    session.add(minimal_show)
    session.commit()
    # THEN show.id should be 1
    assert minimal_show.id == 1


def test_add_full_show_empty_database(database_empty, full_show):
    # GIVEN an initialized empty database
    # WHEN a Show is added
    session = DbSession.factory()
    session.add(full_show)
    session.commit()
    # THEN show.id should be 1
    assert full_show.id == 1


def test_query_all_empty_database(database_empty):
    # GIVEN an initialized empty database
    # WHEN everything is queried
    session = DbSession.factory()
    result = session.query(Show).count()
    session.commit()
    # THEN 0 should be returned
    assert result == 0


def test_add_show_filled_database(database_light, full_show):
    # GIVEN an initialized filled database
    # WHEN a show is added
    session = DbSession.factory()
    session.add(full_show)
    session.commit()
    # THEN show.id should be higher than 10
    assert full_show.id > 10


def test_query_all_filled_database(database_light):
    # GIVEN an initialized and filled database
    # When everything is queried
    session = DbSession.factory()
    result = session.query(Show).count()
    session.commit()
    # THEN more than 10 items should be retrieved
    assert result > 10


@pytest.fixture()
def full_show():
    return Show(
        date_time=arrow.now(),
        title="bla",
        location="theater",
        category="cinema",
        description="wow nice one",
        language_version="OmU",
        dubbed=False,
        url_info="www.theater.com",
        url_tickets="www.buyme.com",
    )


@pytest.fixture()
def minimal_show():
    return Show(
        date_time=arrow.now(), title="bla", location="theater", category="music",
    )
