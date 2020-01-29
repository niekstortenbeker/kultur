"""
Theater classes with methods to update the program by web scraping

Classes
-------
TheaterBase
    Base class for classes representing different theaters
Kinoheld(TheaterBase)
    Theaters that use the Kinoheld website
Filmkunst(Kinoheld):
    Theaters from Filmkunst
Schauburg(Filmkunst):
    Theater Schauburg
Gondel(Filmkunst):
    Theater Gondel
Atlantis(Filmkunst):
    Theater Atlantis
CinemaOstertor(Kinoheld)
    Theater Cinema Ostertor
City46(TheaterBase)
    Theater City 46
TheaterBremen(TheaterBase)
    Theater "TheaterBase Bremen"
Schwankhalle(TheaterBase)
    Theater Schwankhalle
Glocke(TheaterBase)
    Theater Glocke
Kukoon(TheaterBase)
    Theater Kukoon
"""

import bs4
import arrow
import re
import metainfo
import parsing
import webdriver
from program import Program
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
    update_program()
        update the program of this theater by web scraping
    update_meta_info()
        update the meta info of this theater by web scraping
    annotate_dubbed_films()
        update self.program of movie theaters to annotate probably dubbed films
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
        self.meta_info = metainfo.MetaInfo()
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
        self.update_program()
        self.update_meta_info()
        self.annotate_dubbed_films()
        if start_driver:
            webdriver.close_driver()

    def update_program(self):
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

    def update_meta_info(self):
        """
        update self.meta_info by web scraping

        If this method is not overridden by the child class,
        the meta_info is not updated
        """

        pass

    def annotate_dubbed_films(self):
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
        country = show_metainfo["country"].lower()
        if re.search("deutschland|sterreich|schweiz", country):
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


class Kinoheld(TheaterBase):
    """Theaters that use the Kinoheld website

        Attributes
        ----------
        name : str
            the name of the theater
        url : str
            url to the homepage of the theater
        program : Program()
            A program object containing the program of the theater, or an empty Program()
        meta_info : MetaInfo()
            Containing the meta info of the shows in the theater, or an empty MetaInfo()
        url_program_scrape: str
            url to the program used for scraping the program
        url_meta: str
            url used for scraping the meta info

        Methods
        -------
        update_program()
            update the program of this theater by web scraping
        update_meta_info()
            update the meta info of this theater by web scraping
        annotate_dubbed_films()
            update self.program of movie theaters to annotate probably dubbed films
        """

    def __init__(self, name, url, url_program_scrape):
        """
        Parameters
        ----------
        name : str
            the name of the theater
        url : str
            url to the homepage of the theater
        url_program_scrape: str
            url to the program used for scraping the program
        """

        super().__init__(name, url)
        self.url_program_scrape = url_program_scrape

    def _get_shows(self):
        """
        Make a new show list by web scraping the program

        Returns
        -------
        list
            a show list that can be used as shows attribute of Program()
        """

        url = self.url_program_scrape
        html = webdriver.get_html_ajax(url, "movie.u-px-2.u-py-2")
        print(f"{self.html_msg}{url}")
        return self._extract_show_list(html)

    def _extract_show_list(self, html):
        """
        Make a new show list from the source html

        Parameters
        ----------
        html: str
            html source containing the program

        Returns
        -------
        list
            a show list that can be used as shows attribute of Program()
        """

        show_list = []
        soup = bs4.BeautifulSoup(html, "html.parser")
        shows = soup.find_all("article")
        for s in shows:
            date_time = s.find(class_="movie__date").text
            month, day = int(date_time[6:8]), int(date_time[3:5])
            hour, minute = int(date_time[10:12]), int(date_time[13:15])
            date_time = parsing.parse_date_without_year(month, day, hour, minute)
            show = {"date_time": date_time}
            title = s.find(class_="movie__title").text.strip()
            if title[-3:] in ["OmU", " OV", "mdU", "meU"]:
                title = title[:-3].strip()
            show["title"] = title
            if s.find(class_="movie__title").span:
                lang_ver = s.find(class_="movie__title").span.text.strip()
                show["language_version"] = lang_ver
            elif "opera" in title.lower():
                show["language_version"] = "Opera"
            else:
                show["language_version"] = ""
            show["link_tickets"] = "https://www.kinoheld.de/" + s.a.get("href")
            show["link_info"] = self.url
            show["location"] = self.name
            show_list.append(show)
        return show_list


class Filmkunst(Kinoheld):
    """Theaters from Filmkunst (Schauburg, Gondel, Atlantis)

            Attributes
            ----------
            name : str
                the name of the theater
            url : str
                url to the homepage of the theater
            program : Program()
                A program object containing the program of the theater, or an empty Program()
            meta_info : MetaInfo()
                Containing the meta info of the shows in the theater, or an empty MetaInfo()
            url_program_scrape: str
                url to the program used for scraping the program
            url_meta: str
                url used for scraping the meta info

            Methods
            -------
            update_program()
                update the program of this theater by web scraping
            update_meta_info()
                update the meta info of this theater by web scraping
            annotate_dubbed_films()
                update self.program of movie theaters to annotate probably dubbed films
            """

    def __init__(self, name, url, url_program_scrape, url_meta):
        """
        Parameters
        ----------
        name : str
            the name of the theater
        url : str
            url to the homepage of the theater
        url_program_scrape: str
            url to the program used for scraping the program
        url_meta: str
            url used for scraping the meta info
        """

        super().__init__(name, url, url_program_scrape)
        self.url_meta = url_meta

    def update_meta_info(self):
        """
        update self.meta_info by web scraping
        """

        print(f"\n updating meta info {self.name}")
        button_classes = [
            "ui-button.ui-corners-bottom-left.ui-ripple.ui-button--secondary.u-flex-grow-1",
            "ui-button.ui-corners-bottom.ui-ripple.ui-button--secondary.u-flex-grow-1",
        ]
        overlay_class = "overlay-container"
        try:
            html = webdriver.get_html_buttons(self.url_meta, button_classes, overlay_class)
            print(f"{self.html_msg}{self.url_meta}")
            meta = self._extract_meta(html)
            self.meta_info = metainfo.MetaInfo(meta)
        except Exception as e:
            statement = f"Note! Meta info from {self.name} was not updated because of an error. {e}"
            print(statement)

    def _extract_meta(self, html):
        """
        update self.meta_info by web scraping

        note: metainfo["country"] is lazily the first 100 characters of description.

        Parameters
        ----------
        html: str
            html source containing the meta info

        Returns
        -------
        dict
            A dictionary that can be used as shows attribute of a MetaInfo()
        """

        meta_info = {}
        soup = bs4.BeautifulSoup(html, "html.parser")
        films = soup.find_all("article")
        for film in films:
            try:
                dls = film.find_all("dl")
                dt = [t.text.strip().lower() for t in parsing.list_nested_tag(dls, "dt")]
                dd = [t.text.strip() for t in parsing.list_nested_tag(dls, "dd")]
                description = film.find("div", class_="movie__info-description").text
                meta_film = {"title": dd[dt.index("titel")],
                             "description": description,
                             }
            except AttributeError:  # in case there is not enough information for the meta database, such as no <dd>
                continue
            meta_film["country"] = meta_film["description"][0:100]
            if "dauer" in dt:
                meta_film["duration"] = dd[dt.index("dauer")]
            if "genre" in dt:
                meta_film["genre"] = dd[dt.index("genre")]
            if "originaltitel" in dt:
                meta_film["title_original"] = dd[dt.index("originaltitel")]
            if "erscheinungsdatum" in dt:
                meta_film["year"] = dd[dt.index("erscheinungsdatum")][-4:]
            img_screenshot = film.find("div", class_="movie__scenes")
            if img_screenshot:
                img_screenshot = img_screenshot.find_all("img")
                meta_film["img_screenshot"] = [
                    img.get("data-src").strip() for img in img_screenshot
                ]
            img_poster = film.find("div", class_="movie__image")
            if img_poster:
                img_poster = img_poster.find("img").get("src").strip()
                meta_film["img_poster"] = f"{img_poster}"
            meta_info[meta_film["title"]] = meta_film
        return meta_info


class Schauburg(Filmkunst):
    def __init__(self):
        super().__init__(
            name="Schauburg",
            url="http://www.bremerfilmkunsttheater.de/Kino_Reservierungen/Schauburg.html",
            url_program_scrape="https://www.kinoheld.de/kino-bremen/schauburg-kino-bremen/shows/shows?mode=widget",
            url_meta="https://www.kinoheld.de/kino-bremen/schauburg-kino-bremen/shows/movies?mode=widget",
        )


class Gondel(Filmkunst):
    def __init__(self):
        super().__init__(
            name="Gondel",
            url="http://www.bremerfilmkunsttheater.de/Kino_Reservierungen/Gondel.html",
            url_program_scrape="https://www.kinoheld.de/kino-bremen/gondel-filmtheater-bremen/shows/shows?mode=widget",
            url_meta="https://www.kinoheld.de/kino-bremen/gondel-filmtheater-bremen/shows/movies?mode=widget",
        )


class Atlantis(Filmkunst):
    def __init__(self):
        super().__init__(
            name="Atlantis",
            url="http://www.bremerfilmkunsttheater.de/Kino_Reservierungen/Atlantis.html",
            url_program_scrape="https://www.kinoheld.de/kino-bremen/atlantis-filmtheater-bremen/shows/shows?mode=widget",
            url_meta="https://www.kinoheld.de/kino-bremen/atlantis-filmtheater-bremen/shows/movies?mode=widget",
        )


class CinemaOstertor(Kinoheld):
    """Theater Cinema Ostertor

    Attributes
    ----------
    name : str
        the name of the theater
    url : str
        url to the homepage of the theater
    program : Program()
        A program object containing the program of the theater, or an empty Program()
    meta_info : MetaInfo()
        Containing the meta info of the shows in the theater, or an empty MetaInfo()
    url_program_scrape: str
        url to the program used for scraping the program
    url_meta: str
        url used for scraping the meta info

    Methods
    -------
    update_program()
        update the program of this theater by web scraping
    update_meta_info()
        update the meta info of this theater by web scraping
    annotate_dubbed_films()
        update self.program of movie theaters to annotate probably dubbed films
    """

    # TODO use url from meta info for program_link
    def __init__(self):
        url = "https://cinema-ostertor.de/programm"
        super().__init__(
            name="Cinema Ostertor",
            url=url,
            url_program_scrape="https://www.kinoheld.de/kino-bremen/cinema-im-ostertor-bremen/shows/shows?mode=widget",
        )
        self.url_meta = url

    def update_meta_info(self):
        """
        update self.meta_info by web scraping

        For Cinema Ostertor I prefer to use the meta info provided by Cinema Ostertor,
        not by Kinoheld.
        """

        print(f"\n updating meta info {self.name}")
        try:
            urls = self._get_meta_urls()
            meta = self._extract_meta(urls)
            self.meta_info = metainfo.MetaInfo(meta)
        except Exception as e:
            statement = f"Note! Meta info from {self.name} was not updated because of an error. {e}"
            print(statement)

    def _get_meta_urls(self):
        """
        Collect the urls that contain meta info

        Returns
        -------
        set
            a set of urls as str
        """

        html = webdriver.get_html(self.url_meta)
        print(f"{self.html_msg}{self.url_meta}")
        soup = bs4.BeautifulSoup(html, "html.parser")
        urls = [
            url.get("href").strip()
            for url in soup.find_all("a", class_="elementor-post__read-more")
        ]
        return set(urls)

    def _extract_meta(self, movie_urls):
        """
        Update self.meta_info by web scraping

        Parameters
        ----------
        movie_urls: iterable
            Iterable containing urls to meta info as str

        Returns
        -------
        dict
            A dictionary that can be used as shows attribute of a MetaInfo()
        """

        meta_info_program = {}
        for url in movie_urls:
            html = webdriver.get_html(url)
            print(f"{self.html_msg}{url}")
            try:
                meta_info_show = self._parse_show(html)
                meta_info_program[meta_info_show["title"]] = meta_info_show
            except TypeError:
                print(f"No meta info was extracted because of a NoneType (url: {url})")
        return meta_info_program

    def _parse_show(self, html):
        """
        parse show meta info

        Parameters
        ----------
        html: str
            html source code containing one show meta info

        Returns
        -------
        dict or None
            Dictionary contains one show meta info, that when combined in a dictionary
            can serve as the shows attribute of a MetaInfo().
        """

        soup = bs4.BeautifulSoup(html, "html.parser")
        # many stats are hidden in a sloppy bit of html
        # in case there is a web page that doesn't display a normal film have this bit in a try except block
        try:
            stats = soup.find("div", class_="elementor-element-bf542d7")
            d = {}
            for strong in stats.find_all("strong"):
                name = strong.previous_sibling.strip().lower()
                description = strong.text.strip()
                d[name] = description
        except AttributeError:
            return None
        translate = {
            "title_original": "originaler titel:",
            "country": "produktion:",
            "year": "erscheinungsdatum:",
            "genre": "genre:",
            "duration": "dauer:",
            "director": "regie:",
        }
        try:
            meta_film = {"title": d["titel:"]}
        except KeyError:  # If I can't parse the title I don't want anything
            return None
        for key in translate.keys():
            try:
                meta_film[key] = d[translate[key]]
            except KeyError:
                continue
        # do some necessary cleaning
        if "year" in meta_film:
            meta_film["year"] = meta_film["year"][-4:]
        if "duration" in meta_film:
            meta_film["duration"] = meta_film["duration"].replace("\xa0", " ")
        poster = soup.find("div", class_="elementor-element-f5652a8")
        meta_film["img_poster"] = poster.find("img").get("src").strip()
        meta_film["description"] = soup.find("p").text
        return meta_film


class TheaterBremen(TheaterBase):
    """Theater "Theater Bremen"

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

    Methods
    -------
    update_program()
        update the program of this theater by web scraping
    update_meta_info()
        this method does not change anything for Theater Bremen
    annotate_dubbed_films()
        this method does not change anything for Theater Bremen
    """

    def __init__(self):
        super().__init__("Theater Bremen", "http://www.theaterbremen.de")

    def _get_shows(self):
        """
        Make a new show list by web scraping the program

        Returns
        -------
        list
            a show list that can be used as shows attribute of Program()
        """

        shows = []
        urls = self._get_urls()
        for url in urls:
            html = webdriver.get_html_ajax(url, class_name="day")
            print(f"{self.html_msg}{url}")
            shows.extend(self._extract_show_list(html))
        return shows

    def _get_urls(self):
        """
        Get the program url from this month, if date > 20 also get next month

        Returns
        -------
        list
           a list with the urls as str
        """

        urls = []
        date = arrow.now("Europe/Berlin")
        year, month, day = date.year, date.month, date.day
        urls.append("{}#?d={}-{}-{}&f=a".format(self.url, year, month, day))
        if day > 20:
            date = date.shift(months=+1)
            year, month = date.year, date.month
            urls.append("{}#?d={}-{}-{}&f=a".format(self.url, year, month, 20))
        return urls

    def _extract_show_list(self, html):
        """
        Make a new show list from the source html

        Parameters
        ----------
        html: str
            html source containing the program

        Returns
        -------
        list
            a show list that can be used as shows attribute of Program()
        """

        show_list = []
        soup = bs4.BeautifulSoup(html, "html.parser")
        days = soup.find_all(class_="day")
        for day in days:
            date = day.find(class_="date").text.strip()[-10:]
            shows = day.find_all("article")
            for show in shows:
                show = self._extract_show(date, show)
                show_list.append(show)
        return show_list

    def _extract_show(self, date, s):
        """
        parse show information

        Parameters
        ----------
        date: str
        s: bs4.BeautifulSoup()

        Returns
        -------
        dict
            a show dictionary that can be used in a Program().shows
        """

        show = {}
        time = s.find(class_="overview-date-n-flags").text.strip()[0:5]
        date_time = arrow.get(date + time, "DD.MM.YYYYHH:mm", tzinfo="Europe/Berlin")
        show["date_time"] = date_time
        links = s.find_all("a")
        show["link_info"] = f"{self.url}{links[1].get('href').strip()}"
        try:
            show["link_tickets"] = links[2].get("href").strip()
            show["price"] = links[2].text.strip()
        except IndexError:
            pass
        show["title"] = links[1].text.strip()
        info = "".join([info.text for info in s.find_all("p")])
        show["info"] = info.replace("\n", " / ")
        show["location"] = self.name
        return show


class Schwankhalle(TheaterBase):
    """Theater Schwankhalle

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

    Methods
    -------
    update_program()
        update the program of this theater by web scraping
    update_meta_info()
        this method does not change anything for Schwankhalle
    annotate_dubbed_films()
        this method does not change anything for Schwankhalle
    """

    def __init__(self):
        super().__init__("Schwankhalle", "http://schwankhalle.de/spielplan-1.html")

    def _get_shows(self):
        """
        Make a new show list by web scraping the program

        Returns
        -------
        list
            a show list that can be used as shows attribute of Program()
        """

        # at some point requests starting giving SSLError so use selenium for ajax
        html = webdriver.get_html_ajax(self.url, "date-container")
        print(f"{self.html_msg}{self.url}")
        return self._extract_show_list(html)

    def _extract_show_list(self, html):
        """
        Make a new show list from the source html

        Parameters
        ----------
        html: str
            html source containing the program

        Returns
        -------
        list
            a show list that can be used as shows attribute of Program()
        """

        show_list = []
        soup = bs4.BeautifulSoup(html, "html.parser")

        year = soup.find("td", class_="year-month").text.strip()[0:4]
        table = soup.find("table")
        for row in table.find_all("tr"):  # normal for row in table did not work
            if isinstance(row, str):  # skip empty table rows
                continue
            # going to assume that a program row always has a time cell
            if not row.find(class_="time-container"):
                continue
            if not row.find(class_="date-container"):  # solves nonetype errors
                continue
            show = self._extract_show(row, year)
            show_list.append(show)
        return show_list

    def _extract_show(self, row, year):
        """
        parse show information

        Parameters
        ----------
        row: bs4.Beautifulsoup()
            shows are separted on html table rows
        year: str

        Returns
        -------
        a show dictionary that can be used in Program().shows
        """

        show = {"date_time": self._get_date_time(row, year)}
        title_artist_info = row.find("td", class_="title")
        artist = title_artist_info.a.span.text
        # title is not separated by tags:
        title = title_artist_info.a.text[len(artist) + 1:]
        # info is not separated by tags:
        info = title_artist_info.text[len(title) + 1:].strip()
        show["info"] = info.replace("\n", " / ").replace("\t", "")
        show["artist"] = artist.strip()
        show["title"] = title.strip()
        link = "https://schwankhalle.de/{}".format(row.a.get("href").strip())
        show["link_info"] = link
        show["link_tickets"] = link
        show["location"] = self.name
        return show

    def _get_date_time(self, row, year):
        date = row.find(class_="date-container").text.strip()
        date = date + year
        time = row.find(class_="time-container").text.strip()
        time = time[-9:-4]  # in case the time is 'ab ...'
        if not time:
            time = "09:00"
        date_time = arrow.get(date + time, "D.M.YYYYhh:mm", tzinfo="Europe/Berlin")
        return date_time


class Glocke(TheaterBase):
    """Theater Glocke

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

    Methods
    -------
    update_program()
        update the program of this theater by web scraping
    update_meta_info()
        this method does not change anything for Glocke
    annotate_dubbed_films()
        this method does not change anything for Glocke
    """

    def __init__(self):
        super().__init__("Glocke", "https://www.glocke.de/")

    def _get_shows(self):
        """
        Make a new show list by web scraping the program

        Returns
        -------
        list
            a show list that can be used as shows attribute of Program()
        """

        urls = self._get_urls()
        shows = []
        for url in urls:
            html = webdriver.get_html(url)
            print(f"{self.html_msg}{url}")
            shows.extend(self._extract_show_list(html))
        return shows

    def _get_urls(self):
        """
        Get the program url from this and next month

        Returns
        -------
        list
           a list with the urls as str
        """

        arw = arrow.now()
        url1 = self.url + f"/de/Veranstaltungssuche/{arw.month}/{arw.year}"
        arw = arw.shift(months=+1)
        url2 = self.url + f"/de/Veranstaltungssuche/{arw.month}/{arw.year}"
        urls = [url1, url2]
        return urls

    def _extract_show_list(self, html):
        """
        Make a new show list from the source html

        Parameters
        ----------
        html: str
            html source containing the program

        Returns
        -------
        list
            a show list that can be used as shows attribute of Program()
        """

        show_list = []
        soup = bs4.BeautifulSoup(html, "html.parser")
        shows = soup.find_all("div", class_="va-liste")
        for s in shows:
            show = {}
            date_time, location_details = self._get_date_time_and_location_details(s)
            show["date_time"] = date_time
            show["location_details"] = location_details
            title = str(s.find("h2")).strip().replace("<h2>", "")
            title = title.replace("</h2>", "").replace("<br/>", " - ")
            show["title"] = title
            link = self.url + "{}".format(s.a.get("href"))
            show["link_info"] = link
            show["link_tickets"] = link
            show["location"] = self.name
            show_list.append(show)
        return show_list

    def _get_date_time_and_location_details(self, show):
        day = int(show.find(class_=re.compile(r"va_liste_datum_1")).text.strip())
        month = show.find(class_=re.compile(r"va_liste_datum_2")).text.strip().lower()
        months = {
            "jan": 1,
            "feb": 2,
            "mär": 3,
            "maer": 3,
            "märz": 3,
            "apr": 4,
            "mai": 5,
            "jun": 6,
            "jul": 7,
            "aug": 8,
            "sep": 9,
            "sept": 9,
            "okt": 10,
            "nov": 11,
            "dez": 12,
        }
        month = months[month]
        time_location = show.find("span", style=re.compile(r"color")).text.strip()
        hour, minute = int(time_location[:2]), int(time_location[3:6])
        date_time = parsing.parse_date_without_year(month, day, hour, minute)
        location_details = time_location[10:]
        return date_time, location_details


class Kukoon(TheaterBase):
    """Theater Kukoon

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

    Methods
    -------
    update_program()
        update the program of this theater by web scraping
    update_meta_info()
        this method does not change anything for Kukoon
    annotate_dubbed_films()
        this method does not change anything for Kukoon
    """

    def __init__(self):
        super().__init__("Kukoon", "https://kukoon.de/programm/")

    def _get_shows(self):
        """
        Make a new show list by web scraping the program

        Returns
        -------
        list
            a show list that can be used as shows attribute of Program()
        """

        html = webdriver.get_html(self.url)
        print(f"{self.html_msg}{self.url}")
        return self._extract_show_list(html)

    def _extract_show_list(self, html):
        """
        Make a new show list from the source html

        Parameters
        ----------
        html: str
            html source containing the program

        Returns
        -------
        list
            a show list that can be used as shows attribute of Program()
        """

        show_list = []
        soup = bs4.BeautifulSoup(html, "html.parser")
        shows = soup.find_all("div", class_="event")
        for s in shows:
            date_time = s.time
            title_link = s.find(class_="event__title").a
            if not date_time:
                continue
            if "geschlossene gesellschaft" in title_link.text.lower():
                continue
            show = {"date_time": arrow.get(date_time.get("datetime"))}
            show["link_info"] = title_link.get("href")
            show["title"] = title_link.text.strip()
            location_details = s.find(class_="event__venue").text.strip()
            if not location_details == self.name:
                show["location_details"] = location_details
            show["info"] = s.find(class_="event__categories").text.strip()
            show["location"] = self.name
            show_list.append(show)
        return show_list


class City46(TheaterBase):
    """Theater City 46

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

    Methods
    -------
    update_program()
        update the program of this theater by web scraping
    update_meta_info()
        update the meta info of this theater by web scraping
    annotate_dubbed_films()
        update self.program of movie theaters to annotate probably dubbed films
    """

    def __init__(self):
        super().__init__("City 46", "http://www.city46.de/programm/")

    def _get_shows(self):
        """
        Make a new show list by web scraping the program

        Returns
        -------
        list
            a show list that can be used as shows attribute of Program()
        """

        shows = []
        urls, years = self._get_urls()
        for url, year in zip(urls, years):
            html = webdriver.get_html(url)
            print(f"{self.html_msg}{url}")
            table = self._get_program_table(html)
            shows.extend(self._extract_show_list(table, str(year)))
        return shows

    def _get_urls(self):
        """
        Get the program url from this month, if date > 20 also get next month

        Returns
        -------
        list
            a list with the urls as str
        list
            a list with the years as int
        """

        months = {
            1: "januar",
            2: "februar",
            3: "maerz",
            4: "april",
            5: "mai",
            6: "juni",
            7: "juli",
            8: "august",
            9: "september",
            10: "oktober",
            11: "november",
            12: "dezember",
        }
        urls, years = [], []
        date = arrow.now("Europe/Berlin")
        year, month, day = date.year, date.month, date.day
        urls.append(f"{self.url}{months[month]}-{year}.html")
        years.append(year)
        if day > 20:
            date = date.shift(months=+1)
            year, month = date.year, date.month
            urls.append(f"{self.url}{months[month]}-{year}.html")
            years.append(year)
        return urls, years

    def _get_program_table(self, html):
        """the program table is made of several tables that should be combined"""

        soup = bs4.BeautifulSoup(html, "html.parser")
        table = soup.find_all('table')
        table.pop(0)  # first table is not part of program
        return parsing.list_nested_tag(table, 'tr')  # get table rows

    def _extract_show_list(self, table, year):
        """
        Make a new show list from the source html

        Parameters
        ----------
        table: list
            list of html <tr> elements
        year: str

        Returns
        -------
        list
            a show list that can be used as shows attribute of Program()
        """

        date = ''
        show_list = []
        for row in table:
            columns = row.find_all('td')
            if columns[1].text:  # date is not repeated every time, sometimes empty cells
                date = columns[1].text
            try:
                time = columns[2].text
                show = {'date_time': arrow.get(year + date + time, "YYYYD.M.hh:mm", tzinfo="Europe/Berlin"),
                        'title': columns[3].a.text,
                        'location': self.name,
                        'info': self._get_info(columns)
                        }
                link = columns[3].a
            except (AttributeError, arrow.parser.ParserMatchError):
                continue
            if link.get('class')[0] == 'internal-link':
                show['link_info'] = "http://www.city46.de/" + link.get("href")
            else:
                show['link_info'] = link.get("href")
            if columns[3].dfn:
                show['language_version'] = columns[3].dfn.text
            show_list.append(show)
        return show_list

    def _get_info(self, columns):
        """info can be in the fourth column (where also the title is) or in the fifth column"""

        if columns[3].br:
            info = columns[3].br.next.strip()
            if info.endswith(','):
                info = info[:-1]
        else:
            info = ''
        if columns[4].text:
            info = info + '. ' + columns[4].text
        return info