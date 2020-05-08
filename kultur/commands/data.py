import os
from pathlib import Path
from typing import List

from arrow import Arrow
from kultur.data.dbsession import DbSession
from kultur.data.fake_data import complete_program
from kultur.data.fake_data import program as fake_program
from kultur.data.show import Show
from kultur.data.showsgetter import ShowsGetter


def init_database():
    """
    Initialize the database.

    An initialized database is required for all the other functions.
    The database only needs to be initialized once.
    """
    database = Path.home() / ".kultur" / "kultur.sqlite"
    if not database.parent.exists():
        # noinspection PyTypeChecker
        os.mkdir(database.parent)
    DbSession.global_init(str(database.resolve()))


def get_shows(
    start: Arrow, stop: Arrow, category: str, dubbed: bool, location: str = ""
) -> List[Show]:
    """
    Query shows from database.

    Requires an initialized database.

    Parameters
    ----------
    start: Arrow
        From this point in time shows will be retrieved
    stop: Arrow
        To this point in time shows will be retrieved
    category: str
        Should be "all", "cinema", "music" or "stage"
    dubbed: bool
        If True also return dubbed films, if False exclude dubbed films
    location: str, optional
        Either name of location or '' for all locations

    Returns
    -------
    List[Show]
        A list with show objects ordered by Show.date_time.

    """
    shows = ShowsGetter(start, stop, category, dubbed, location)
    return shows.get()


def fake_data():
    """populate database with fake data"""
    session = DbSession.factory()
    program = complete_program(fake_program)
    session.add_all(program)
    session.commit()


def get_location_names():
    """
    Get all possible Show.location_name_url mapped to Show.location

    This can be used to convert a location name from e.g. a request
    to a name that can be used for querying the database with get_shows()

    Returns
    -------
    dict[str: str]
        possible Show.location_name_url names mapped to their
        Show.location attributes
    """
    # note: use kultur.update.theaters.all for this dict
    return {
        "schauburg": "Schauburg",
        "gondel": "Gondel",
        "atlantis": "Atlantis",
        "cinemaostertor": "Cinema Ostertor",
        "city46": "City 46",
        "theaterbremen": "Theater Bremen",
        "schwankhalle": "Schwankhalle",
        "glocke": "Glocke",
        "kukoon": "Kukoon",
    }
