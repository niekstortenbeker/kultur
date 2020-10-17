import os
from typing import List

from arrow import Arrow
from kultur.data import fake_data
from kultur.data.dbsession import DbSession
from kultur.data.show import Show
from kultur.data.showsgetter import ShowsGetter


def init_database():
    """
    Initialize the database.

    An initialized database is required for all the other functions.
    The database only needs to be initialized once.
    """
    user = os.environ["kultur_database_user"]
    password = os.environ["kultur_database_password"]
    db = os.environ["kultur_database_name"]
    DbSession.global_init(user, password, db)


def init_fake_database():
    """
    Initialize a database and populate with fake data.

    An initialized database is required for all the other functions.
    The database only needs to be initialized once.
    """
    DbSession.global_init_fake_data()


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
        "alle": "",
    }


if __name__ == "__main__":
    init_database()
    print(DbSession.factory)
    session = DbSession.factory()
    session.query(Show).delete()
    program = fake_data.complete_program(fake_data.program)
    session.add_all(program)
    session.commit()
    print(session.query(Show).all())
