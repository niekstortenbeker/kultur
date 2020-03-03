import re
from helper import webdriver
from program.program import Program
from program.metainfo import MetaInfo
import emoji


class TheaterBase:
    """
    Base class for classes representing different theaters

    Attributes
    ----------
    name : str
        the name of the theater
    url : str
        url that links the user to the theater (homepage or program page)
    program : Program()
        A program object containing the program of the theater, or an empty Program()
    meta_info : MetaInfo()
        Containing the meta info of the shows in the theater, or an empty MetaInfo()
    html_msg: str
        Base message for printing that a html was obtained, should be appended with
        the name of the url.

    Methods
    -------
    update_program_and_meta_info(self, start_driver=False):
        update the program and meta_info of this theater by web scraping
    """

    def __init__(self, name, url):
        """
        Parameters
        ----------
        name : str
            the name of the theater
        url : str
            url that links the user to the theater (homepage or program page)
        """

        self.name = name
        self.url = url
        self.program = Program()
        self.meta_info = MetaInfo()
        self.html_msg = emoji.emojize(f"    :tada: Retrieved html from: ",
                                      use_aliases=True)

    def __repr__(self):
        return f"TheaterBase({self.name, self.url})"

    def __str__(self):
        return f"TheaterBase({self.name})"

    def update_program_and_meta_info(self, start_driver=False):
        """
        update the program and meta_info of this theater by web scraping

        This will also annotate dubbed films in program

        Parameters
        ----------
        start_driver: bool, optional
            if False (=default) might require driver to be started as 'driver',
            when True a selenium driver will be started.
        """

        if start_driver:
            webdriver.start_driver()
        self._update_program()
        self._update_meta_info()
        self._annotate_dubbed_films()
        if start_driver:
            webdriver.close_driver()

    def _update_program(self):
        """
        update the program of this theater by web scraping

        uses _get_shows() which should be an available method in each child
        class.
        """
        print(f"\n updating program {self.name}")
        try:
            shows = self._get_shows()
            self.program = Program(shows)
            self.program.sort()
        except Exception as e:
            print(
                f"Note! Program from {self.name} was not updated because of an error {e}"
            )

    def _get_shows(self):
        """
        Make a new show list by web scraping the program

        Note: this is a dummy method that should be overridden by child classes

        Returns
        -------
        list
            a show list that can be used as shows attribute of Program()
        """

        print("Note! _get_shows() should be present in the child class")
        return []

    def _update_meta_info(self):
        """
        update self.meta_info by web scraping

        If this method is not overridden by the child class,
        the meta_info is not updated
        """

        pass

    def _annotate_dubbed_films(self):
        """
        update self.program of movie theaters to annotate probably dubbed films

        Only changes movie theaters.
        For each show in self.program, add the key "is_probably_dubbed_film",
        with the value True or False.
        """
        if self.name not in ["Schauburg", "Gondel", "Atlantis", "Cinema Ostertor"]:
            return
        for s in self.program:
            try:
                if self._film_is_probably_dubbed(s):
                    s["is_probably_dubbed_film"] = True
                else:
                    s["is_probably_dubbed_film"] = False
            except AttributeError as e:
                s["is_probably_dubbed_film"] = True
                date = f"{s.get('date_time').month}-{s.get('date_time').day}"
                print(f"    \"{s.get('title')}\" | {date} was set to be a dubbed movie due to missing data ({e})")

    def _film_is_probably_dubbed(self, show):
        """
        evaluates if a movie is likely to be dubbed

        Movies that are Omu or OV etc are not dubbed, and movies that seem
        to be made in a german speaking country are considered not dubbed

        Parameters
        ----------
        show: dictionary
            a show dictionary (see Program())

        Returns
        -------
        bool
            True when film is probably dubbed
        """

        if show.get("language_version", False):  # OMUs and OV
            return False
        elif self._is_german(show["title"]):  # should be in child
            return False
        else:
            return True

    def _is_german(self, title):
        """
        evaluates if the movie is likely to be german

        movie is considered german when it's made in a german speaking country
        and the title and original title are equal

        Parameters
        ----------
        title: str
            title of a show (as used in Program() or MetaInfo())

        Raises
        ------
        AttributeError
            when no meta information is found

        Returns
        -------
        bool
            returns True when the movie is likely to be german
        """

        show_metainfo = self.meta_info.get(title)
        if not show_metainfo:
            raise AttributeError('No meta info found')
        country = show_metainfo.get("country")
        if not country:
            raise AttributeError('No meta info found')
        if re.search("deutschland|sterreich|schweiz", country.lower()):
            title = show_metainfo.get("title")
            title_original = show_metainfo.get("title_original")
            if not title_original:  # if no original title info is available
                return True
            elif title.strip().lower() == title_original.strip().lower():
                return True
            else:  # a different original title suggests it is dubbed after all
                return False
        else:
            return False


