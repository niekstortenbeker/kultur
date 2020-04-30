import pytest
from kultur.data import fake_data
from kultur.data.dbsession import DbSession
from kultur.data.fake_data import complete_program
from kultur.data.show import Show
from kultur.update.services import webdriver


@pytest.fixture(scope="session")
def started_webdriver():
    webdriver.start_driver()
    yield
    webdriver.close_driver()


@pytest.fixture(scope="session")
def database_empty_dir(tmpdir_factory):
    """initialize and close empty database, return directory"""
    tmpdir = tmpdir_factory.mktemp("temp")
    database_dir = str(tmpdir.join("kultur.sqlite"))
    DbSession.global_init(database_dir)
    DbSession.close()
    return database_dir


@pytest.fixture()
def database_empty(database_empty_dir):
    """when a empty database that can be altered is required"""
    DbSession.global_init(database_empty_dir)
    session = DbSession.factory()
    session.query(Show).delete()
    session.commit()

    yield

    DbSession.close()


@pytest.fixture()
def database_light(database_empty):
    """when a lightly filled database that can be altered is required"""
    session = DbSession.factory()
    session.add_all(complete_program(fake_data.light_program))
    session.commit()


@pytest.fixture()
def database_full(database_full_dir):
    DbSession.global_init(database_full_dir)

    yield

    DbSession.close()


@pytest.fixture(scope="session")
def database_full_dir(tmpdir_factory):
    """add many records, so only do once per session, return directory"""
    tmpdir = tmpdir_factory.mktemp("temp")
    database_dir = str(tmpdir.join("kultur.sqlite"))
    DbSession.global_init(database_dir)
    session = DbSession.factory()
    program = complete_program(fake_data.program)
    session.add_all(program)
    session.commit()
    DbSession.close()
    return database_dir
