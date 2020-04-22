import pytest
from kultur.update.theaters.all import all_theaters
from kultur.update.theaters.theaterbase import TheaterBase

theater_ids = [theater.name for theater in all_theaters]


@pytest.mark.parametrize("theater", all_theaters, ids=theater_ids)
@pytest.mark.online
def test_program_is_updated(theater: TheaterBase, started_webdriver):
    # GIVEN a started webdriver
    # WHEN TheaterBase.update_program() is called
    theater.update_program()
    # THEN a program should be set
    assert len(theater.program) > 1
