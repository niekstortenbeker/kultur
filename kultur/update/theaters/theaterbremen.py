import arrow
import bs4
from kultur.data.show import Show
from kultur.update.services import webdriver
from kultur.update.theaters.theaterbase import TheaterBase

Tag = bs4.element.Tag
Arrow = arrow.arrow.Arrow


class TheaterBremen(TheaterBase):
    def __init__(self):
        url = "http://www.theaterbremen.de"
        super().__init__("Theater Bremen", url, url_program=url)

    def _scrape_program(self):
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
            print(f"{self._html_msg}{url}")
            shows.extend(self._extract_show_list(html))
        self.program = shows

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
        urls.append("{}#?d={}-{}-{}&f=a".format(self.url_program, year, month, day))
        if day > 20:
            date = date.shift(months=+1)
            year, month = date.year, date.month
            urls.append("{}#?d={}-{}-{}&f=a".format(self.url_program, year, month, 20))
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

        show = Show()
        show.date_time = _get_date_time(date, s)
        links = s.find_all("a")
        show.url_info = f"{self.url}{links[1].get('href').strip()}"
        try:
            show.url_tickets = links[2].get("href").strip()
            # show.price = links[2].text.strip()
        except IndexError:
            pass
        show.title = links[1].text.strip()
        show.description = _get_info(s)
        show.location = self.name
        show.category = "stage"
        return show


def _get_date_time(date: str, show: Tag) -> Arrow:
    # noinspection PyUnresolvedReferences
    time = show.find(class_="overview-date-n-flags").text.strip()[0:5]
    date_time = arrow.get(date + time, "DD.MM.YYYYHH:mm", tzinfo="Europe/Berlin")
    return date_time


def _get_info(show: Tag) -> str:
    info = "".join([info.text for info in show.find_all("p")])
    return info.replace("\n", " / ")
