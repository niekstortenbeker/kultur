from typing import List, Union

from data.dbsession import DbSession, UninitializedDatabaseError
from data.show import Show
from update.services import webdriver
from update.theaters.cinemaostertor import CinemaOstertor
from update.theaters.city46 import City46
from update.theaters.filmkunst import Atlantis, Gondel, Schauburg
from update.theaters.glocke import Glocke
from update.theaters.kukoon import Kukoon
from update.theaters.schwankhalle import Schwankhalle
from update.theaters.theaterbase import TheaterBase
from update.theaters.theaterbremen import TheaterBremen

all_theaters = [
    Schauburg(),
    Gondel(),
    Atlantis(),
    CinemaOstertor(),
    City46(),
    TheaterBremen(),
    Schwankhalle(),
    Glocke(),
    Kukoon(),
]


def update_program_all_theaters() -> List[TheaterBase]:
    """scrape program from the web, only return successfully updated theaters"""
    if not DbSession.factory:
        raise UninitializedDatabaseError

    updated_theaters = []
    webdriver.start_driver()
    for theater in all_theaters:
        try:
            theater.update_program()
            updated_theaters.append(theater)
        except Exception as e:
            print(
                f"the program from {theater.name} was not updated because of a {e} error"
            )
            continue
    webdriver.close_driver()
    return updated_theaters


def replace_records(theaters: Union[List[TheaterBase], TheaterBase]) -> int:
    """returns count of added records"""
    if not DbSession.factory:
        raise UninitializedDatabaseError
    if isinstance(theaters, TheaterBase):
        theaters = [theaters]
    elif not isinstance(theaters, List):
        raise TypeError("only excepts TheaterBase or List of Theaterbase")
    elif not isinstance(theaters[0], TheaterBase):
        raise TypeError("only excepts TheaterBase or List of Theaterbase")

    added_records = 0
    session = DbSession.factory()
    for theater in theaters:
        session.query(Show).filter_by(location=theater.name).delete()
        session.add_all(theater.program)
        added_records += len(theater.program)
    session.commit()
    return added_records
