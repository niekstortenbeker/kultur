import arrow
import bs4
from helper import webdriver
from theaters.theaterbase import TheaterBase


class Kukoon(TheaterBase):
    """Theater Kukoon

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
        url = "https://kukoon.de/programm/"
        super().__init__("Kukoon", url, url_program=url)

    def _get_shows(self):
        """
        Make a new show list by web scraping the program

        Returns
        -------
        list
            a show list that can be used as shows attribute of Program()
        """

        html = webdriver.get_html(self.url_program)
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
        shows = soup.find_all("div", class_="event")
        for s in shows:

            date_time = s.time
            title_link = s.find(class_="event__title").a
            if not date_time or "geschlossene gesellschaft" in title_link.text.lower():
                continue

            show = {
                "date_time": arrow.get(date_time.get("datetime")),
                "link_info": title_link.get("href"),
                "title": title_link.text.strip(),
                "info": s.find(class_="event__categories").text.strip(),
                "location": self.name,
            }
            location_details = s.find(class_="event__venue").text.strip()
            if not location_details == self.name:
                show["location_details"] = location_details

            show_list.append(show)
        return show_list