import bs4
from helper import webdriver, parsing
from theaters.theaterbase import TheaterBase


class Kinoheld(TheaterBase):
    """Theaters that use the Kinoheld website

        Attributes
        ----------
        name : str
            the name of the theater
        url : str
            url to the homepage of the theater
        program : Program()
            A program object containing the program of the theater, or an empty Program()
        meta_info : MetaInfo()
            Containing the meta info of the shows in the theater, or an empty MetaInfo()
        url_program: str
            url to the program used for scraping the program
        url_meta: str
            url used for scraping the meta info

        Methods
        -------
        update_program_and_meta_info(self, start_driver=False):
            update the program and meta_info of this theater by web scraping
        """

    def __init__(self, name, url, url_program=None, url_meta=None):
        """
        Parameters
        ----------
        name : str
            the name of the theater
        url : str
            url to the homepage of the theater
        url_program: str
            url to the program used for scraping the program
        """

        super().__init__(name, url, url_program=url_program, url_meta=url_meta)

    def _get_shows(self):
        """
        Make a new show list by web scraping the program

        Returns
        -------
        list
            a show list that can be used as shows attribute of Program()
        """

        url = self.url_program
        html = webdriver.get_html_ajax(url, "movie.u-px-2.u-py-2")
        print(f"{self._html_msg}{url}")
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
        shows = soup.find_all("article")
        for s in shows:
            date_time = s.find(class_="movie__date").text
            month, day = int(date_time[6:8]), int(date_time[3:5])
            hour, minute = int(date_time[10:12]), int(date_time[13:15])
            date_time = parsing.parse_date_without_year(month, day, hour, minute)
            show = {"date_time": date_time}
            title = s.find(class_="movie__title").text.strip()
            if title[-3:] in ["OmU", " OV", "mdU", "meU"]:
                title = title[:-3].strip()
            show["title"] = title
            if s.find(class_="movie__title").span:
                lang_ver = s.find(class_="movie__title").span.text.strip()
                show["language_version"] = lang_ver
            elif "opera" in title.lower():
                show["language_version"] = "Opera"
            else:
                show["language_version"] = ""
            show["link_tickets"] = "https://www.kinoheld.de/" + s.a.get("href")
            show["link_info"] = self.url
            show["location"] = self.name
            show_list.append(show)
        return show_list