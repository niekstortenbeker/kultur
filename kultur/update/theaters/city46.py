import re

import arrow
import bs4
import kultur.update.services.metainfo as mi
from kultur.data import show_defaults
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
                # if a director etc is there add that information to the description
                if show.description and s.find(class_="guest"):
                    show.description = (
                        show.description + " " + s.find(class_="guest").text
                    )
                show.category = "cinema"
                show.url_info = "https://www.city46.de" + s.find("a").get("href")
                # TODO: what to do when the performance is impro?
                if s.find("a", class_="dpnglossary"):
                    show.language_version = s.find("a", class_="dpnglossary").text
                show_list.append(show)
        return show_list

    def _update_meta_info(self):
        """
        update self._meta_info by web scraping

        For Cinema Ostertor I prefer to use the meta info provided by Cinema Ostertor,
        not by Kinoheld.
        """

        print(f"\n updating meta info {self.name}")
        try:
            meta = self._extract_meta_info(self._get_meta_urls())
            self._meta_info = meta
        except Exception as e:
            statement = f"Note! Meta info from {self.name} was not updated because of an error. {e}"
            print(statement)

    def _get_meta_urls(self):
        urls = [program.url_info for program in self.program]
        return set(urls)

    def _extract_meta_info(self, movie_urls):
        """
        Update self._meta_info by web scraping

        Parameters
        ----------
        movie_urls: iterable
            Iterable containing urls to meta info as str

        Returns
        -------
        dict
            a dict that maps titles to MetaInfo()
        """

        meta_info_program = {}
        for url in movie_urls:
            meta_info_show = self._extract_meta_info_show(url)
            if meta_info_show:
                meta_info_program[meta_info_show.title] = meta_info_show
        return meta_info_program

    def _extract_meta_info_show(self, url: str) -> mi.MetaInfo:
        try:
            html = webdriver.get_html(url)
            print(f"{self._html_msg}{url}")
            html_section = url[url.rfind("#") + 1 :]
            return _parse_meta_info_show(html, html_section)
        except TypeError:
            print(f"No meta info was extracted because of a TypeError (url: {url})")
        except AttributeError:
            print(
                f"No meta info was extracted because of a AttributeError (url: {url})"
            )
        except Exception:
            print(f"No meta info was extracted because of an exception (url: {url})")

    def _adjust_show(self, show: Show, meta_info):
        """
        Use the information in metainfo to update all the shows in program
        """
        if not meta_info.description:
            return show
        show.description = show.description + " " + meta_info.description
        show.description_start = show_defaults.make_description_start(show.description)
        show.description_end = show_defaults.make_description_end(
            show.description, show.description_start
        )
        return show


def _parse_meta_info_show(html: str, html_section: str) -> mi.MetaInfo:
    """
    parse show meta info

    Parameters
    ----------
    html: str
        html source code containing one show meta info

    Returns
    -------
    MetaInfo() or None
    """
    soup = bs4.BeautifulSoup(html, "html.parser")
    section = soup.find("div", id=html_section)
    description = section.find("div", class_="filmtext").text.strip()
    title = section.find("div", class_="start-header").text.strip()
    return mi.MetaInfo(description=description, title=title)


if __name__ == "__main__":
    city = City46()
    city.update_program()
    print(city.program)
    print(city.program[0].description)
    print(city.program[0].description_start)
    print(city.program[0].description_end)
