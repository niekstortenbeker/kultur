import re

import bs4
import kultur.update.services.metainfo as mi
from kultur.data import show_defaults
from kultur.update.services import dubbed, webdriver
from kultur.update.theaters.kinoheld import Kinoheld

Tag = bs4.element.Tag
Soup = bs4.BeautifulSoup


class CinemaOstertor(Kinoheld):
    def __init__(self):
        url = "https://cinema-ostertor.de/programm"
        super().__init__(
            name="Cinema Ostertor",
            url=url,
            url_program="https://www.kinoheld.de/kino-bremen/cinema-im-ostertor-bremen/shows/shows?mode=widget",
            url_meta=url,
        )

    def _update_meta_info(self):
        """
        update self._meta_info by web scraping

        For Cinema Ostertor I prefer to use the meta info provided by Cinema Ostertor,
        not by Kinoheld.
        """

        print(f"\n updating meta info {self.name}")
        try:
            meta = self._extract_meta_info(self._get_meta_urls())
            self._meta_info = meta
        except Exception as e:
            statement = f"Note! Meta info from {self.name} was not updated because of an error. {e}"
            print(statement)

    def _adjust_show(self, show, meta_info):
        """
        Use the information in metainfo to update all the shows in program
        """
        show.dubbed = dubbed.is_dubbed(show, meta_info)
        show.description = meta_info.description
        show.description_start = show_defaults.make_description_start(show.description)
        show.description_end = show_defaults.make_description_end(
            show.description, show.description_start
        )
        show.url_info = meta_info.url_info
        return show

    def _get_meta_urls(self):
        """
        Collect the urls that contain meta info

        Returns
        -------
        set
            a set of urls as str
        """

        print(f"{self._html_msg}{self.url_meta}")
        soup = bs4.BeautifulSoup(webdriver.get_html(self.url_meta), "html.parser")
        urls = [
            url.get("href").strip()
            for url in soup.find_all("a", class_="elementor-post__read-more")
        ]
        return set(urls)

    def _extract_meta_info(self, movie_urls):
        """
        Update self._meta_info by web scraping

        Parameters
        ----------
        movie_urls: iterable
            Iterable containing urls to meta info as str

        Returns
        -------
        dict
            a dict that maps titles to MetaInfo()
        """

        meta_info_program = {}
        for url in movie_urls:
            meta_info_show = self._extract_meta_info_show(url)
            if meta_info_show:
                meta_info_program[meta_info_show.title] = meta_info_show
        return meta_info_program

    def _extract_meta_info_show(self, url: str) -> mi.MetaInfo:
        html = webdriver.get_html_ajax(url, "elementor-text-editor.elementor-clearfix")
        print(f"{self._html_msg}{url}")
        try:
            return _parse_meta_info_show(html)
        except TypeError:
            print(f"No meta info was extracted because of a NoneType (url: {url})")


# noinspection PyUnresolvedReferences,PyTypeChecker
def _parse_meta_info_show(html) -> mi.MetaInfo:
    """
    parse show meta info

    Parameters
    ----------
    html: str
        html source code containing one show meta info

    Returns
    -------
    MetaInfo() or None
    """
    soup = bs4.BeautifulSoup(html, "html.parser")
    sections = soup.find_all("section")
    stats = sections[2]
    title = sections[1].text
    if not title:
        return None

    description = (
        sections[3].find("div", id="movie-content-text").text.replace("\n", "")
    )
    return mi.MetaInfo(
        title=title.strip().replace("\n", ""),
        description=_parse_duration(stats) + " " + description,
        country=_parse_item_from_stats(stats, "Land"),
    )


def _parse_item_from_stats(stats: Tag, german_name: str) -> str:
    try:
        # noinspection PyUnresolvedReferences
        item = stats.find(text=re.compile(german_name)).next
        return str(item).strip()
    except AttributeError:
        return ""


def _parse_duration(stats: Tag) -> str:
    try:
        return _parse_item_from_stats(stats, "Laufzeit").replace("\xa0", " ")
    except AttributeError:
        return ""


if __name__ == "__main__":
    cinema_ostertor = CinemaOstertor()
    cinema_ostertor.update_program(start_driver=True)
    print(cinema_ostertor.program)
    print(cinema_ostertor.program[0].description)
    print(cinema_ostertor._meta_info)
