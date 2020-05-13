import arrow
import kultur
import pytest


def test_get_location_names():
    result = kultur.get_location_names()
    assert len(result) > 2


def test_get_shows(database_full):
    result = kultur.get_shows(arrow.now(), arrow.now().shift(days=+1), "all", True)
    assert len(result) > 5


def test_print_today(database_full, capsys):
    kultur.print_today()
    out, err = capsys.readouterr()
    assert len(out) > 1000


def test_print_week(database_full, capsys):
    kultur.print_week()
    out, err = capsys.readouterr()
    assert len(out) > 1000


def test_print_header(capsys):
    kultur.print_header()
    out, err = capsys.readouterr()
    assert len(out) > 1000


@pytest.mark.online
def test_update_program(database_light):
    result = kultur.update_program()
    assert len(result) > 10
