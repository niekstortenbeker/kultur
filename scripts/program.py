"""
Classes
-------
Program
    A Program with a list of shows and display methods
"""

import arrow
from colorama import init
init()
from colorama import Fore, Back, Style


class Program:
    """
    A Program with a list of shows and display methods

    Some shows can also be found in MetaInfo and are identified based on title.

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

        if shows:
            self.shows = shows
            self.date = arrow.now("Europe/Berlin")
        else:
            self.shows = []
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

        print(f"\nThis program uses a database made {self.date.humanize()}")
        if program is None:
            program = self.shows
        if not program:  # empty programs
            print('There are no shows to display')
            return
        old_date = arrow.get(0).date()
        for show in program:
            old_date = self._print_day_separator(old_date, show)
            self._print_show(show)

    def _print_day_separator(self, old_date, show):
        """
        when the show is on a new day print a separator

        Parameters
        ----------
        old_date: datetime.date
            date from the previous show
        show: dict
            a show dictionary (from self.shows)
        """

        date = show["date_time"].date()
        if date != old_date:
            print_date = show['date_time'].format('dddd MM-DD')
            print()
            print(f"{Style.BRIGHT} {print_date} ".center(50, "-"))
            print()
        return date

    def _print_show(self, show):
        """
        print information about one show on one line

        Parameters
        ----------
        show: dict
            a show dictionary (from self.shows)
        """
        film_theaters = ['Schauburg', 'Gondel', 'Atlantis', 'Cinema Ostertor',
                         'City 46']
        if show.get('location') in film_theaters:
            c1 = Back.LIGHTMAGENTA_EX
            c2 = Fore.MAGENTA
        else:
            c1 = Back.LIGHTBLUE_EX
            c2 = Fore.BLUE
        stop = Style.RESET_ALL

        time = show['date_time'].format('HH:mm')
        print(f"{Style.BRIGHT}{time}{stop} | ", end='')
        print(f"{c1}{show.get('location', '')}{stop} | ", end='')
        print(f"{c2}{show.get('artist', '')}{show.get('title', '')}{stop} | ", end='')
        print(f"{show.get('link_info', '')} |", end='')
        print(f"{show.get('info', '')}|", end='')
        print(f"{show.get('price', '')}|")


