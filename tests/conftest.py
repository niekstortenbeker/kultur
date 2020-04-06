import pytest
from typing import List
from tests import fake_data
from data.show import Show
from update.theaters.theaterbase import TheaterBase


@pytest.fixture()
def filled_program(location) -> List[Show]:
    """return can be used as a program from TheaterBase.program"""
    if isinstance(location, TheaterBase):
        location = location.name
    elif type(location) != str:
        TypeError("only TheaterBase or str accepted")

    return [filled_show(location) for _ in range(4 * 30 * 2)]


@pytest.fixture()
def partially_filled_program(location) -> List[Show]:
    """return can be used as a program from TheaterBase.program"""
    if isinstance(location, TheaterBase):
        location = location.name
    elif type(location) != str:
        TypeError("only TheaterBase or str accepted")

    return [partially_filled_show(location) for _ in range(4 * 30 * 2)]


def filled_show(location):
    show = Show()
    show.date_time = fake_data.show_date_time()
    show.title = fake_data.get("title")
    show.location = location
    show.category = fake_data.get("category")
    show.description = fake_data.get("description")
    show.language_version = fake_data.get("language_version")
    show.dubbed = fake_data.get("dubbed")
    show.url_info = fake_data.get("url_info")
    show.url_tickets = fake_data.get("url_tickets")
    return show


def partially_filled_show(location):
    show = Show()
    show.date_time = fake_data.show_date_time()
    show.title = fake_data.get("title")
    show.location = location
    show.category = fake_data.get("category")
    show.description = fake_data.get_value_or_empty("description")
    show.language_version = fake_data.get_value_or_empty("language_version")
    show.dubbed = fake_data.get_value_or_empty("dubbed")
    show.url_info = fake_data.get_value_or_empty("url_info")
    show.url_tickets = fake_data.get_value_or_empty("url_tickets")
    return show


if __name__ == "__main__":
    print(partially_filled_program("Hmmm")[0])
