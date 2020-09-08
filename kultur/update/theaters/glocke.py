import re

import arrow
import bs4
from kultur.data.show import Show
from kultur.update.services import parsing, webdriver
from kultur.update.theaters.theaterbase import TheaterBase

Tag = bs4.element.Tag
Arrow = arrow.arrow.Arrow


class Glocke(TheaterBase):
    def __init__(self):
        url = "https://www.glocke.de"
        super().__init__("Glocke", url, url_program=f"{url}/de/Veranstaltungssuche")

    def _scrape_program(self):
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
            print(f"{self._html_msg}{url}")
            shows.extend(self._extract_show_list(html))
        self.program = shows

    def _get_urls(self):
        """
        Get the program url from this and next month

        Returns
        -------
        list
           a list with the urls as str
        """

        arw = arrow.now()
        url1 = f"{self.url_program}/{arw.month}/{arw.year}"
        arw = arw.shift(months=+1)
        url2 = f"{self.url_program}/{arw.month}/{arw.year}"
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
            show = Show()
            try:
                show.date_time = _get_date_time(s)
            except AttributeError:
                continue

            show.description = _get_description(s)
            show.title = _get_title(s)
            show.url_info = f"{self.url}/{s.a.get('href')}"
            show.location = self.name
            show.category = "music"

            show_list.append(show)
        return show_list


def _get_title(show):
    title = str(show.find("h2")).strip().replace("<h2>", "")
    title = title.replace("</h2>", "").replace("<br/>", " - ")
    return title


def _get_date_time(show: Tag) -> Arrow:
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
    return parsing.parse_date_without_year(month, day, hour, minute)


def _get_description(show: Tag) -> str:
    """description is made of location details and optional hinweise"""
    time_location = show.find("span", style=re.compile(r"color"))
    time_location = time_location.text.strip()[10:] if time_location else ""
    note = show.find("div", class_="va_hinweis")
    note = note.text.strip() if note else ""
    return note + " " + time_location


if __name__ == "__main__":
    glocke = Glocke()
    glocke.update_program()
    for show in glocke.program:
        print(show)
