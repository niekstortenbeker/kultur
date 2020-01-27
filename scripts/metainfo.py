"""
MetaInfo
    Meta information about shows
"""

import arrow


class MetaInfo:
    """
    Meta information about shows

    Shows in meta info can be found (but are not required to) in the shows in
    a program class and are identified by the title.
    Not all shows in a program class are required to be present in a MetaInfo.

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

        if shows:
            self.shows = shows
            self.date = arrow.now("Europe/Berlin")
        else:
            self.shows = {}
            self.date = arrow.get(0)

    def __repr__(self):
        return f"MetaInfo({self.shows})"

    def __str__(self):
        return str(self.shows)

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