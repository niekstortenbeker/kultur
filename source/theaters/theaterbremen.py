import arrow
import bs4
from helper import webdriver
from theaters.theaterbase import TheaterBase


class TheaterBremen(TheaterBase):
    """Theater "Theater Bremen"

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
        super().__init__("Theater Bremen", "http://www.theaterbremen.de")

    def _get_shows(self):
        """
        Make a new show list by web scraping the program

        Returns
        -------
        list
            a show list that can be used as shows attribute of Program()
        """

        shows = []
        urls = self._get_urls()
        for url in urls:
            html = webdriver.get_html_ajax(url, class_name="day")
            print(f"{self.html_msg}{url}")
            shows.extend(self._extract_show_list(html))
        return shows

    def _get_urls(self):
        """
        Get the program url from this month, if date > 20 also get next month

        Returns
        -------
        list
           a list with the urls as str
        """

        urls = []
        date = arrow.now("Europe/Berlin")
        year, month, day = date.year, date.month, date.day
        urls.append("{}#?d={}-{}-{}&f=a".format(self.url, year, month, day))
        if day > 20:
            date = date.shift(months=+1)
            year, month = date.year, date.month
            urls.append("{}#?d={}-{}-{}&f=a".format(self.url, year, month, 20))
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
        days = soup.find_all(class_="day")
        for day in days:
            date = day.find(class_="date").text.strip()[-10:]
            shows = day.find_all("article")
            for show in shows:
                show = self._extract_show(date, show)
                show_list.append(show)
        return show_list

    def _extract_show(self, date, s):
        """
        parse show information

        Parameters
        ----------
        date: str
        s: bs4.BeautifulSoup()

        Returns
        -------
        dict
            a show dictionary that can be used in a Program().shows
        """

        show = {}
        time = s.find(class_="overview-date-n-flags").text.strip()[0:5]
        date_time = arrow.get(date + time, "DD.MM.YYYYHH:mm", tzinfo="Europe/Berlin")
        show["date_time"] = date_time
        links = s.find_all("a")
        show["link_info"] = f"{self.url}{links[1].get('href').strip()}"
        try:
            show["link_tickets"] = links[2].get("href").strip()
            show["price"] = links[2].text.strip()
        except IndexError:
            pass
        show["title"] = links[1].text.strip()
        info = "".join([info.text for info in s.find_all("p")])
        show["info"] = info.replace("\n", " / ")
        show["location"] = self.name
        return show