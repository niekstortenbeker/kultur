from typing import Callable, List

import pytest
from kultur.data.dbsession import DbSession
from kultur.data.show import Show
from kultur.update.data import all_theaters
from tests import fake_data

shows = List[Show]


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


def complete_program(theater_program: Callable[[str], shows]) -> shows:
    """theater_program is function from view.test_data.py (light or full)"""
    theaters = all_theaters.copy()
    program = []
    for theater in theaters:
        program.extend(theater_program(theater.name))
    return program
