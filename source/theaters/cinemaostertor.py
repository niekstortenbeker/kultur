import re
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
    update_program_and_meta_info(self, start_driver=False):
        update the program and meta_info of this theater by web scraping
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
            html = webdriver.get_html_ajax(url, "elementor-text-editor.elementor-clearfix")
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
        meta_film = {}
        soup = bs4.BeautifulSoup(html, "html.parser")
        stats = soup.find("div", class_="elementor-element-bf542d7")

        title = self._parse_item_from_stats(stats, 'Titel')
        if not title:
            return None

        meta_film['title'] = title
        meta_film['title_original'] = self._parse_item_from_stats(stats, 'Originaler Titel')
        meta_film['country'] = self._parse_item_from_stats(stats, 'Produktion')
        meta_film['genre'] = self._parse_item_from_stats(stats, 'Genre')
        meta_film['duration'] = self._parse_item_from_stats(stats, 'Dauer')
        meta_film['director'] = self._parse_item_from_stats(stats, 'Regie')
        meta_film["description"] = soup.find(role="document").text

        year = self._parse_item_from_stats(stats, 'Erscheinungsdatum')
        if year:
            meta_film["year"] = year[-4:]
        duration = self._parse_item_from_stats(stats, 'Dauer')
        if duration:
            meta_film["duration"] = duration.replace("\xa0", " ")
        poster = soup.find("div", class_="elementor-element-f5652a8")
        if poster:
            meta_film["img_poster"] = poster.find("img").get("src").strip()
        return meta_film

    def _parse_item_from_stats(self, stats, german_name):
        try:
            return stats.find(text=re.compile(german_name)).next.text.strip()
        except AttributeError:
            return None
