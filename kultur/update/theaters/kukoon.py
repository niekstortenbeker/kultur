from typing import Union

import arrow
import bs4
from kultur.data.show import Show
from kultur.update.services import webdriver
from kultur.update.theaters.theaterbase import TheaterBase

Tag = bs4.element.Tag


class Kukoon(TheaterBase):
    def __init__(self):
        url = "https://kukoon.de/programm/"
        super().__init__("Kukoon", url, url_program=url)

    def _scrape_program(self):
        """
        Make a new show list by web scraping the program

        Returns
        -------
        list
            a show list that can be used as shows attribute of Program()
        """

        html = webdriver.get_html(self.url_program)
        print(f"{self._html_msg}{self.url_program}")
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
        shows = soup.find_all("div", class_="event")
        for s in shows:

            date_time = s.time
            title_link = s.find(class_="event__title").a
            if not date_time or "geschlossene gesellschaft" in title_link.text.lower():
                continue

            show = Show()
            show.date_time = arrow.get(date_time.get("datetime"))
            show.url_info = title_link.get("href")
            show.title = title_link.text.strip()
            category, description = _get_category_and_description(s)
            show.category = category
            show.description = description
            show.location = self.name

            location_details = s.find(class_="event__venue").text.strip()
            if not location_details == self.name:
                show.location_details = location_details

            show_list.append(show)
        return show_list


def _get_category_and_description(s: Tag) -> (str, Union[None, str]):
    # noinspection PyUnresolvedReferences
    category = s.find(class_="event__categories").text
    if "kino" in category.lower():
        return "cinema", None
    elif "konzert" in category.lower():
        return "music", None
    else:
        return (
            "stage",
            category.replace("Veranstaltungskategorie:", "")
            .replace("Veranstaltungskategorien:", "")
            .strip(),
        )
