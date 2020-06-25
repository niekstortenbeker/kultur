import re

import arrow
import bs4
from kultur.data.show import Show
from kultur.update.services import webdriver
from kultur.update.theaters.theaterbase import TheaterBase


class City46(TheaterBase):
    def __init__(self):
        url = "https://www.city46.de/programm/"
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
            shows.extend(self._extract_show_list(html, str(year)))
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
        urls.append(f"{self.url_program}{months[month]}-{year}")
        years.append(year)
        if day > 20:
            date = date.shift(months=+1)
            year, month = date.year, date.month
            urls.append(f"{self.url_program}{months[month]}-{year}")
            years.append(year)
        return urls, years

    def _extract_show_list(self, html, year):
        soup = bs4.BeautifulSoup(html, "html.parser")
        days = soup.find_all("div", class_="termintabelle")
        show_list = []
        for day in days:
            date = day.find("div", class_="termin_header").text
            date = re.search(r"\d\d?\.\d\d?\.", date)
            if not date:
                continue
            date = date[0]

            for s in day.find_all("div", class_="tercon_content"):
                time = s.find(class_="tercon_time").text.strip()
                if not time:
                    continue
                if not s.find("a"):
                    continue

                show = Show()
                show.date_time = arrow.get(
                    year + date + time, "YYYYD.M.hh:mm", tzinfo="Europe/Berlin"
                )
                show.title = s.find(class_="tercon_titel").text.strip()
                show.location = self.name
                show.description = s.find(class_="tercon_credits").text.strip()
                if s.find(class_="guest"):  # if a director etc is there
                    show.description = (
                        show.description + " " + s.find(class_="guest").text
                    )
                show.category = "cinema"
                show.url_info = "http://www.city46.de" + s.find("a").get("href")
                # TODO: what to do when the performance is impro?
                if s.find("a", class_="dpnglossary"):
                    show.language_version = s.find("a", class_="dpnglossary").text
                show_list.append(show)
        return show_list


if __name__ == "__main__":
    city = City46()
    city._scrape_program()
