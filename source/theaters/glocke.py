import re
import arrow
import bs4
from helper import webdriver, parsing
from theaters.theaterbase import TheaterBase


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
    update_program_and_meta_info(self, start_driver=False):
        update the program and meta_info of this theater by web scraping
    """

    def __init__(self):
        url = "https://www.glocke.de"
        super().__init__("Glocke", url, url_program=f'{url}/de/veranstaltungssuche')

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
            print(f"{self._html_msg}{url}")
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
            show = {}
            date_time, location_details = self._get_date_time_and_location_details(s)
            show["date_time"] = date_time
            show["location_details"] = location_details
            title = str(s.find("h2")).strip().replace("<h2>", "")
            title = title.replace("</h2>", "").replace("<br/>", " - ")
            show["title"] = title
            link = f"{self.url}/{s.a.get('href')}"
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