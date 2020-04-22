from typing import Union

import arrow
import bs4
from kultur.data.show import Show
from kultur.update.services import parsing, webdriver
from kultur.update.theaters.theaterbase import TheaterBase

Tag = bs4.element.Tag
Arrow = arrow.arrow.Arrow


class Kinoheld(TheaterBase):
    def __init__(self, name, url, url_program=None, url_meta=None):
        """
        Parameters
        ----------
        name : str
            the name of the theater
        url : str
            url to the homepage of the theater
        url_program: str
            url to the program used for scraping the program
        """

        super().__init__(name, url, url_program=url_program, url_meta=url_meta)

    def _scrape_program(self):
        """
        Make a new show list by web scraping the program

        Returns
        -------
        list
            a show list that can be used as shows attribute of Program()
        """

        url = self.url_program
        html = webdriver.get_html_ajax(url, "movie.u-px-2.u-py-2")
        print(f"{self._html_msg}{url}")
        self.program = self._extract_show_list(html)

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
            try:
                show = Show()
                show.date_time = _get_date_time(s)
                show.title = _get_title(s)
            except AttributeError:
                continue

            show.language_version = _get_language_version(s, show.title)
            show.url_tickets = "https://www.kinoheld.de/" + s.a.get("href")
            show.url_info = self.url
            show.location = self.name
            show.category = "cinema"

            show_list.append(show)
        return show_list


def _get_title(show: Tag) -> Arrow:
    # noinspection PyUnresolvedReferences
    title = show.find(class_="movie__title").text.strip()
    if title[-3:] in ["OmU", " OV", "mdU", "meU"]:
        title = title[:-3].strip()
    return title


def _get_date_time(show: Tag) -> Arrow:
    # noinspection PyUnresolvedReferences
    date_time = show.find(class_="movie__date").text
    month, day = int(date_time[6:8]), int(date_time[3:5])
    hour, minute = int(date_time[10:12]), int(date_time[13:15])
    date_time = parsing.parse_date_without_year(month, day, hour, minute)
    return date_time


def _get_language_version(show: Tag, title) -> Union[str, None]:
    # noinspection PyUnresolvedReferences
    language_version = show.find(class_="movie__title").span
    if language_version:
        return language_version.text.strip()
    elif "opera" in title.lower():
        return "Opera"
