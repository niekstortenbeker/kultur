import pytest
from data.dbsession import DbSession
from tests import fake_data
from update.data import all_theaters


@pytest.fixture()
def database_empty(tmpdir):
    DbSession.global_init(str(tmpdir / "kultur.sqlite"))

    yield

    DbSession.close()


@pytest.fixture()
def database_light(database_empty, complete_program_light):
    session = DbSession.factory()
    session.add_all(complete_program_light)
    session.commit()

    yield


@pytest.fixture()
def complete_program_light():
    theaters = all_theaters.copy()
    program = []
    for theater in theaters:
        theater_program = fake_data.light_program(theater.name)
        program.extend(theater_program)
    return program


