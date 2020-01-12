"""
Collect (web scraping) and combine programs from theaters in Bremen

It is probably best to interact with this module using CombinedProgram.
A CombinedProgram has a Program containing shows from all theaters, and
has a list of Theaters which each have an individual Program and
MetaInfo. Programs can be updated from file or by web scraping.

Classes
-------
CombinedProgram
    A combined program of a selection of theaters in Bremen
Program
    A Program with a list of shows and display methods
MetaInfo
    Meta information about shows
"""

import copy
import arrow
import file
import helper
from theater import Filmkunst, CinemaOstertor, City46, TheaterBremen, Schwankhalle, Glocke, Kukoon


class CombinedProgram:
    """
    A combined program of a selection of theaters in Bremen

    ...
    Attributes
    ----------
    theaters : list
        A list of Theater() objects with individual program attributes
    program : Program()
        A combined program from all the theaters

    Methods
    -------
    program_from_file()
        Use the program from the data stored on file
    update_program()
        Update the program from the web and replace the program on file
    """

    def __init__(self):
        schauburg = Filmkunst(
            name="Schauburg",
            url="http://www.bremerfilmkunsttheater.de/Kino_Reservierungen/Schauburg.html",
            url_program_scrape="https://www.kinoheld.de/kino-bremen/schauburg-kino-bremen/shows/shows?mode=widget",
            url_meta="https://www.kinoheld.de/kino-bremen/schauburg-kino-bremen/shows/movies?mode=widget",
        )
        gondel = Filmkunst(
            name="Gondel",
            url="http://www.bremerfilmkunsttheater.de/Kino_Reservierungen/Gondel.html",
            url_program_scrape="https://www.kinoheld.de/kino-bremen/gondel-filmtheater-bremen/shows/shows?mode=widget",
            url_meta="https://www.kinoheld.de/kino-bremen/gondel-filmtheater-bremen/shows/movies?mode=widget",
        )
        atlantis = Filmkunst(
            name="Atlantis",
            url="http://www.bremerfilmkunsttheater.de/Kino_Reservierungen/Atlantis.html",
            url_program_scrape="https://www.kinoheld.de/kino-bremen/atlantis-filmtheater-bremen/shows/shows?mode=widget",
            url_meta="https://www.kinoheld.de/kino-bremen/atlantis-filmtheater-bremen/shows/movies?mode=widget",
        )
        cinema_ostertor = CinemaOstertor()
        city_46 = City46()
        theater_bremen = TheaterBremen()
        schwankhalle = Schwankhalle()
        glocke = Glocke()
        kukoon = Kukoon()
        self.theaters = [
            schauburg,
            gondel,
            atlantis,
            cinema_ostertor,
            city_46,
            theater_bremen,
            schwankhalle,
            glocke,
            kukoon,
        ]
        self.program = Program()

    def __repr__(self):
        return "CombinedProgram()"

    def program_from_file(self):
        """
        Use the program from the data stored on file

        First the program and meta of each theater in self.theaters are
        updated, and then self.program is built from these.
        """

        program, meta, date = file.open_from_file()
        # program and meta are dictionaries with the theater names as
        # keys and the show lists as values
        for t in self.theaters:
            if t.name in program:
                t.program = Program(shows=program[t.name])
                t.program.date = date
        for t in self.theaters:
            if t.name in meta:
                t.meta_info = MetaInfo(shows=meta[t.name])
                t.meta_info.date = date
        self._refresh_program(date=date)

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

    # TODO make method that can update one theater only
    def update_program(self):
        """
        Update the program from the web and replace the program on file

        The program is updated both in the theater.program of self.theaters,
        and in self.program.
        """

        # update program
        helper.start_driver()
        for t in self.theaters:
            t.update_program()
        # update meta info
        for t in self.theaters:
            t.update_meta_info()
            t.annotate_dubbed_films()
        helper.close_driver()
        self._refresh_program(date=arrow.now())
        self._program_to_file()

    def _refresh_program(self, date):
        """
        make a new self.program based on the programs in self.theaters
        """

        self.program.empty()
        for t in self.theaters:
            try:
                self.program = self.program + t.program
            except AttributeError:  # if theater has None as program
                continue
        self.program.sort()
        self.program.date = date


class Program:
    """
    A Program with a list of shows and display methods

    Some shows can also be found in MetaInfo and are identified based on title.
    When setting the shows attribute also set the date attribute.  # TODO force this behaviour

    ...
    Attributes
    ----------
    shows : list of dictionaries, optional
        A list of show dictionaries, which should have the key:
        date_time : arrow datetime object
        It could have the following keys:
        title : str
            is used to crosslink with shows in MetaInfo
        artist : str
        link_info : str
        link_tickets : str
        location_details : str
            in case a theater has multiple venues
        location : str
            name of the theater
        info : str
        price : str
        language_version : str
    date : arrow datetime object
        date on which program was scraped

    Methods
    -------
    empty()
        Replace shows with an empty list
    sort()
        Sort shows ascending in time
    print_next_week()
        Print the program of the next week from now
    print_today()
        Print the program of today
    print(program=None)
        Print the complete program, or a custom show list when provided as argument
    """

    def __init__(self, shows=None):
        """
        Parameters
        ----------
        shows : list of dictionaries, optional
            A list of show dictionaries, which should have the key:
            date_time : arrow datetime object
            It could have the following keys:
            title : str
                is used to crosslink with shows in MetaInfo
            artist : str
            link_info : str
            link_tickets : str
            location_details : str
                in case a theater has multiple venues
            location : str
                name of the theater
            info : str
            price : str
            language_version : str
        """

        self.shows = shows if shows else []
        self.date = arrow.get(0)

    def __repr__(self):
        return f"Program({self.shows})"

    def __str__(self):
        return str(self.shows)

    def __add__(self, other):
        shows = self.shows + other.shows
        return Program(shows)

    def __len__(self):
        return len(self.shows)

    def __iter__(self):
        return iter(self.shows)

    def __contains__(self, item):
        return item in [s["title"] for s in self.shows]

    def empty(self):
        """Replace shows with an empty list"""

        self.shows = []

    def sort(self):
        """ Sort shows ascending in time"""

        self.shows.sort(key=lambda show: show["date_time"])

    def print_next_week(self):
        """Print the program of the next week from now"""

        now = arrow.utcnow()
        stop_day = now.shift(weeks=+1).replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo="Europe/Berlin"
        )
        self.print(program=self._filter_program(stop_day))

    def print_today(self):
        """Print the program of today"""

        now = arrow.utcnow()
        stop_day = now.shift(days=+1).replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo="Europe/Berlin"
        )
        self.print(program=self._filter_program(stop_day))

    def _filter_program(self, stop_day):
        """
        filter a subset of the program between now and stop_day

        Parameters
        ----------
        stop_day : arrow.arrow.Arrow
            the day and time until which the program should be filtered

        Returns
        -------
        list
            a list with the filtered show dictionaries
        """

        program = []
        now = arrow.now("Europe/Berlin")
        for show in self.shows:
            if show["date_time"] < now:
                continue
            elif show["date_time"] > stop_day:
                break
            elif show.get("is_probably_dubbed_film"):
                continue
            else:
                program.append(show)
        return program

    def print(self, program=None):
        """
        Print the complete program, or a custom show list when provided as argument

        Parameters
        ----------
        program : list, optional
            a list with show dictionaries similar to self.shows
        """
        print(f"\nthis program uses a database made {self.date.humanize()}")
        print("".center(50, "-"))
        if program is None:
            program = self.shows
        if not program:  # empty programs
            print('There are no shows to display')
            return
        old_day = program[0]["date_time"].date()
        for s in program:
            # print day separator
            day = s["date_time"].date()
            if day != old_day:
                print("".center(50, "-"))
                old_day = day
            # print program
            print(
                "{} | {} | {} {} | {} | {} | {}".format(
                    s["date_time"].format("ddd MM-DD HH:mm"),
                    s.get("location", ""),
                    s.get("artist", ""),
                    s.get("title", ""),
                    s.get("link_info", ""),
                    s.get("info", ""),
                    s.get("price", ""),
                )
            )


class MetaInfo:
    """
    Meta information about shows

    Shows in meta info can be found (but are not required to) in the shows in
    a program class and are identified by the title.
    Not all shows in a program class are required to be present in a MetaInfo.
    When setting the shows attribute also set the date attribute.  # TODO force this behaviour

    ...
    Attributes
    ----------
    shows : dict of dicts, optional
        A dict with titles as keys and show meta info dicts as values.
        These titles can be used to crosslink to a show in a Program().
        Show meta info dicts could have the following keys:
        title : str
        title_original : str
        country : str
        year : int
        genre : str
        duration : str
        director : str
        language : str
        description : str
        img_poster : str
            hyperlink to the image
        ing_screenshot : str
            hyperlink to the image
        link_info : str
    date : arrow datetime object
        Date on which the meta info was scraped

    Methods
    -------
    get(title)
        get a show by title
    """

    def __init__(self, shows=None):
        """
        Parameters
        ----------
        shows : dict of dicts, optional
            A dict with titles as keys and show meta info dicts as values.
            These titles can be used to crosslink to a show in a Program().
            Show meta info dicts could have the following keys:
            title : str
            title_original : str
            country : str
            year : int
            genre : str
            duration : str
            director : str
            language : str
            description : str
            img_poster : str
                hyperlink to the image
            ing_screenshot : str
                hyperlink to the image
            link_info : str
        """

        self.shows = shows if shows else {}
        self.date = arrow.get(0)

    def __repr__(self):
        return f"MetaInfo({self.shows})"

    def __str__(self):
        return str(self.shows)

    def __add__(self, other):
        shows = self.shows + other.shows
        return Program(shows)

    def __len__(self):
        return len(self.shows)

    def __iter__(self):
        return iter(self.shows)

    def __contains__(self, item):
        return item in self.shows

    def get(self, title):
        """
        get a show by title

        Parameters
        ----------
        title : str

        Returns
        -------
        dict
            a meta info dictionary which could have the following keys:
            title : str
            title_original : str
            country : str
            year : int
            genre : str
            duration : str
            director : str
            language : str
            description : str
            img_poster : str
                hyperlink to the image
            ing_screenshot : str
                hyperlink to the image
            link_info : str
        """

        return self.shows.get(title)