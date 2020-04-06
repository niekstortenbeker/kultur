import arrow
import bs4
from update.services import webdriver
from update.theaters.theaterbase import TheaterBase


# noinspection PyUnresolvedReferences
class Schwankhalle(TheaterBase):
    def __init__(self):
        url = "http://schwankhalle.de/spielplan-1.html"
        super().__init__("Schwankhalle", url, url_program=url)

    def _scrape_program(self):
        """
        Make a new show list by web scraping the program

        Returns
        -------
        list
            a show list that can be used as shows attribute of Program()
        """

        # at some point requests starting giving SSLError so use selenium for ajax
        html = webdriver.get_html_ajax(self.url_program, "date-container")
        print(f"{self._html_msg}{self.url_program}")
        self.shows = self._extract_show_list(html)

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
        row: bs4.element.Tag
            shows are separted on html table rows
        year: str

        Returns
        -------
        a show dictionary that can be used in Program().shows
        """

        title_artist_info = row.find("td", class_="title")
        artist = title_artist_info.a.span.text
        # title is not separated by tags:
        title = title_artist_info.a.text[len(artist) + 1 :]
        # info is not separated by tags:
        info = title_artist_info.text[len(title) + 1 :].strip()

        show = Show()
        show.date_time = _get_date_time(row, year)
        show.description = info.replace("\n", " / ").replace("\t", "")
        show.title = title.strip() + " - " + artist.strip()
        show.url_info = "https://schwankhalle.de/{}".format(row.a.get("href").strip())
        show.location = self.name
        show.category = "stage"
        return show


def _get_date_time(row, year):
    date = row.find(class_="date-container").text.strip()
    date = date + year
    time = row.find(class_="time-container").text.strip()
    time = time[-9:-4]  # in case the time is 'ab ...'
    if not time:
        time = "09:00"
    date_time = arrow.get(date + time, "D.M.YYYYhh:mm", tzinfo="Europe/Berlin")
    return date_time
