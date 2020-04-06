import arrow
import bs4

from data.show import Show
from update.services import webdriver, parsing
from update.theaters.theaterbase import TheaterBase


class City46(TheaterBase):
    def __init__(self):
        url = "http://www.city46.de/programm/"
        super().__init__("City 46", url, url_program=url)

    def _scrape_program(self):
        """
        Make a new show list by web scraping the program

        Returns
        -------
        list
            a show list that can be used as shows attribute of Program()
        """

        shows = []
        urls, years = self._get_urls()
        for url, year in zip(urls, years):
            html = webdriver.get_html(url)
            print(f"{self._html_msg}{url}")
            table = self._get_program_table(html)
            shows.extend(self._extract_show_list(table, str(year)))
        self.program = shows

    def _get_urls(self):
        """
        Get the program url from this month, if date > 20 also get next month

        Returns
        -------
        list
            a list with the urls as str
        list
            a list with the years as int
        """

        months = {
            1: "januar",
            2: "februar",
            3: "maerz",
            4: "april",
            5: "mai",
            6: "juni",
            7: "juli",
            8: "august",
            9: "september",
            10: "oktober",
            11: "november",
            12: "dezember",
        }
        urls, years = [], []
        date = arrow.now("Europe/Berlin")
        year, month, day = date.year, date.month, date.day
        urls.append(f"{self.url_program}{months[month]}-{year}.html")
        years.append(year)
        if day > 20:
            date = date.shift(months=+1)
            year, month = date.year, date.month
            urls.append(f"{self.url_program}{months[month]}-{year}.html")
            years.append(year)
        return urls, years

    def _get_program_table(self, html):
        """the program table is made of several tables that should be combined"""

        soup = bs4.BeautifulSoup(html, "html.parser")
        table = soup.find_all("table")
        table.pop(0)  # first table is not part of program
        return parsing.list_nested_tag(table, "tr")  # get table rows

    def _extract_show_list(self, table, year):
        """
        Make a new show list from the source html

        Parameters
        ----------
        table: list
            list of html <tr> elements
        year: str

        Returns
        -------
        list
            a show list that can be used as shows attribute of Program()
        """

        date = ""
        show_list = []
        for row in table:
            columns = row.find_all("td")
            if columns[
                1
            ].text:  # date is not repeated every time, sometimes empty cells
                date = columns[1].text
            try:
                time = columns[2].text
                show = Show()
                show.date_time = arrow.get(
                    year + date + time, "YYYYD.M.hh:mm", tzinfo="Europe/Berlin"
                )
                show.title = columns[3].a.text
                show.location = (self.name,)
                show.description = _get_info(columns)
                show.category = "cinema"

                link = columns[3].a
            except (AttributeError, arrow.parser.ParserMatchError):
                continue
            if link.get("class")[0] == "internal-link":
                show.url_info = "http://www.city46.de/" + link.get("href")
            else:
                show.url_info = link.get("href")
            if columns[3].dfn:
                show.language_version = columns[3].dfn.text
            show_list.append(show)
        return show_list


def _get_info(columns):
    """info can be in the fourth column (where also the title is) or in the fifth column"""

    if columns[3].br:
        info = columns[3].br.next.strip()
        if info.endswith(","):
            info = info[:-1]
    else:
        info = ""
    if columns[4].text:
        info = info + ". " + columns[4].text
    return info
