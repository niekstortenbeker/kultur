"""
Combined Program class

A CombinedProgram has a Program containing shows from all theaters, and
has a list of Theaters which each have an individual Program and
MetaInfo.

Classes
-------
CombinedProgram
    A combined program of a selection of theaters in Bremen
"""

import copy
import arrow
from database import file
from helper import webdriver
from theaters.filmkunst import Schauburg, Gondel, Atlantis
from theaters.cinemaostertor import CinemaOstertor
from theaters.city46 import City46
from theaters.theaterbremen import TheaterBremen
from theaters.schwankhalle import Schwankhalle
from theaters.glocke import Glocke
from theaters.kukoon import Kukoon
from program.program import Program
from program.metainfo import MetaInfo


class CombinedProgram:
    """
    A combined program of a selection of theaters in Bremen

    When initiated it will try to load a previously scraped program
    from disk.

    ...
    Attributes
    ----------
    theaters : list
        A list of TheaterBase() objects with individual program and
        meta_info attributes
    program : Program()
        A combined program from all the theaters

    Methods
    -------
    update_program()
        Update the program from the web and replace the program on file
    """

    def __init__(self):
        self.theaters = [
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
        self.program = Program()
        self._program_from_file()

    def __repr__(self):
        return "CombinedProgram()"

    def update_program(self):
        """
        Update the program from the web and replace the program on file

        The program is updated both in the theater.program of self.theaters,
        and in self.program.
        """

        webdriver.start_driver()
        for theater in self.theaters:
            theater.update_program_and_meta_info()
        webdriver.close_driver()
        self._refresh_program(date=arrow.now())
        self._program_to_file()

    def _refresh_program(self, date):
        """
        make a new self.program based on the programs in self.theaters
        """

        self.program.empty()
        for theater in self.theaters:
            try:
                self.program = self.program + theater.program
            except AttributeError:  # if theater has None as program
                continue
        self.program.sort()
        self.program.date = date

    def _program_to_file(self):
        """
        store the current program to file, replacing the old files

        For all self.theaters, make one file that combines the program.shows
        as a dictionary with theater names as keys and the program.shows
        as values, and one file similarly for meta_info.shows.
        """

        program_db = {t.name: t.program.shows for t in self.theaters}
        program_db = copy.deepcopy(program_db)  # no changing of the original data
        meta_db = {t.name: t.meta_info.shows for t in self.theaters}
        meta_db = copy.deepcopy(meta_db)
        file.save_to_file(program_db, meta_db)

    def _program_from_file(self):
        """
        Use the program from the data stored on file

        First the program and meta of each theater in self.theaters are
        updated, and then self.program is built from these.
        """

        try:
            program, meta, date = file.open_from_file()
        except FileNotFoundError:  # in case files are not there
            return
        # program and meta are dictionaries with the theater names as
        # keys and the show lists as values
        for theater in self.theaters:
            if theater.name in program:
                theater.program = Program(shows=program[theater.name])
                theater.program.date = date
        for theater in self.theaters:
            if theater.name in meta:
                theater.meta_info = MetaInfo(shows=meta[theater.name])
                theater.meta_info.date = date
        self._refresh_program(date=date)