import bs4
from helper import webdriver
from program.metainfo import MetaInfo
from theaters.kinoheld import Kinoheld


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
    _update_program()
        update the program of this theater by web scraping
    _update_meta_info()
        update the meta info of this theater by web scraping
    _annotate_dubbed_films()
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

    def _update_meta_info(self):
        """
        update self.meta_info by web scraping

        For Cinema Ostertor I prefer to use the meta info provided by Cinema Ostertor,
        not by Kinoheld.
        """

        print(f"\n updating meta info {self.name}")
        try:
            urls = self._get_meta_urls()
            meta = self._extract_meta(urls)
            self.meta_info = MetaInfo(meta)
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
                meta_info_show = self._parse_meta_info_show(html)
                meta_info_program[meta_info_show["title"]] = meta_info_show
            except TypeError:
                print(f"No meta info was extracted because of a NoneType (url: {url})")
        return meta_info_program

    def _parse_meta_info_show(self, html):
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