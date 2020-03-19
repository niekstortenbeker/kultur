import arrow
import bs4
from helper import webdriver
from theaters.theaterbase import TheaterBase


class Schwankhalle(TheaterBase):
    """Theater Schwankhalle

    Attributes
    ----------
    name : str
        the name of the theater
    url : str
        url that links the user to the theater (homepage or program page)
    url_program : str
        url used to scrape the program
    url_meta : str
        url used to scrape the meta_info
    program : Program()
        A program object containing the program of the theater, or an empty Program()
    meta_info : MetaInfo()
        Containing the meta info of the shows in the theater, or an empty MetaInfo()

    Methods
    -------
    update_program_and_meta_info(self, start_driver=False):
        update the program and meta_info of this theater by web scraping
    """

    def __init__(self):
        url = "http://schwankhalle.de/spielplan-1.html"
        super().__init__("Schwankhalle", url, url_program=url)

    def _get_shows(self):
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