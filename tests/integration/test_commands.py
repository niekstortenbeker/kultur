import pytest
from kultur.commands import data, update, view
from kultur.data.dbsession import DbSession
from kultur.view import data as view_data
from kultur.view import display


@pytest.mark.online
def test_update_program(database_empty):
    # GIVEN an initialized empty database
    # WHEN program is updated
    update.update_program()
    # THEN a program for next week should be retrieved from database
    result = view_data.get_program_week()
    assert len(result) > 1


def test_print_week(database_full, mocker):
    # GIVEN an initialized and full database
    # WHEN commands.view.print_week() is called
    mocker.patch.object(display, "print_program")
    view.print_week()
    # THEN view.display.print_program() should be called once
    # noinspection PyUnresolvedReferences
    view.display.print_program.assert_called_once()


def test_print_today(database_full, mocker):
    # GIVEN an initialized and full database
    # WHEN commands.view.print_today() is called
    mocker.patch.object(display, "print_program")
    view.print_today()
    # THEN view.display.print_program() should be called once
    # noinspection PyUnresolvedReferences
    view.display.print_program.assert_called_once()


def test_init_database():
    # GIVEN no database is initialized
    # WHEN init_database() is called
    data.init_database()
    # THEN a database should be initialized
    assert DbSession.factory is not None
    DbSession.close()
