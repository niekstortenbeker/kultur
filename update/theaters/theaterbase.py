from update.services import webdriver
import emoji


class TheaterBase:
    """
    Base class for classes used to update de program of different theaters

    Attributes
    ----------
    name : str
        the name of the theater
    url : str
        url that links the user to the theater homepage
    url_program : str
        url that links to the program for user or scraping
    url_meta: str
        url that links to meta info for scraping
    program: list
        list of Show objects
    _meta_info: dict
        a dict that maps titles to MetaInfo(), can be used to adjust program
    _html_msg: str
        Base message for printing that a html was obtained, should be appended with
        the name of the url.

    Methods
    -------
    update_program_all_theaters(self, start_driver=False):
        update the program and meta_info of this theater by web scraping
    """

    def __init__(self, name, url, url_program=None, url_meta=None):
        """
        Parameters
        ----------
        name : str
            the name of the theater
        url : str
            url that links the user to the theater homepage
        url_program : str, optional
            url that links to the program for user or scraping
        url_meta: str, optional
            url that links to meta info for scraping
        """

        self.name = name
        self.url = url
        self.url_program = url_program
        self.url_meta = url_meta
        self.program = []
        self._meta_info = {}
        self._html_msg = emoji.emojize(
            f"    :tada: Retrieved html from: ", use_aliases=True
        )

    def __repr__(self):
        return f"Theater({self.name, self.program})"

    def __str__(self):
        return f"Theater({self.name})"

    def update_program(self, start_driver=False):
        """
        update the program and meta_info of this theater by web scraping

        This will also annotate dubbed films in program

        Parameters
        ----------
        start_driver: bool, optional
            if False (=default) might require driver to be started as 'driver',
            when True a selenium driver will be started.
        """
        print(f"\n updating program {self.name}")
        if start_driver:
            webdriver.start_driver()
        self._scrape_program()
        self._update_meta_info()
        self._adjust_program_from_meta_info()
        if start_driver:
            webdriver.close_driver()

    def _scrape_program(self):
        """
        Update self.program
        should be implemented by subclasses
        """
        raise NotImplementedError

    def _update_meta_info(self):
        """
        update self.meta_info by web scraping. Useful if _scrape_program() does not
        provide enough information

        If this method is not overridden by the child class,
        the meta_info is not updated
        """
        pass

    def _adjust_program_from_meta_info(self):
        """
        Use the information in metainfo to update all the shows in program
        """
        if not self._meta_info:
            return

        not_updated = set()

        for idx, show in enumerate(self.program):
            meta_info = self._meta_info.get(show.title, None)
            if not meta_info:
                not_updated.add(show)
                continue
            self.program[idx] = self._adjust_show(show, meta_info)

        for show in not_updated:
            print(f"{show.title} was not adjusted due to missing meta information")

    def _adjust_show(self, show, meta_info):
        """
        Use the information in metainfo to update show

        If this method is not overridden by the child class,
        nothing is adjusted
        """
        return show
