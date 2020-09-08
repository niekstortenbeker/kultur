import re

import bs4
from kultur.data import show_defaults
from kultur.update.services import dubbed, webdriver
from kultur.update.services.metainfo import MetaInfo
from kultur.update.theaters.kinoheld import Kinoheld

Tag = bs4.element.Tag


class Filmkunst(Kinoheld):
    def __init__(self, name, url, url_program, url_meta):
        """
        name : str
            the name of the theater
        url : str
            url that links the user to the theater (homepage or program page)
        url_program : str
            url used to scrape the program
        url_meta : str
            url used to scrape the meta_info
        """
        super().__init__(name, url, url_program=url_program, url_meta=url_meta)

    def _update_meta_info(self):
        """
        update self._meta_info by web scraping

        For Cinema Ostertor I prefer to use the meta info provided by Cinema Ostertor,
        not by Kinoheld.
        """

        print(f"\n updating meta info {self.name}")
        try:
            meta = self._extract_meta_info()
            self._meta_info = meta
        except Exception as e:
            statement = f"Note! Meta info from {self.name} was not updated because of an error. {e}"
            print(statement)

    def _extract_meta_info(self):
        """
        Update self._meta_info by web scraping

        Returns
        -------
        dict
            a dict that maps titles to MetaInfo()
        """
        meta_info_program = {}
        html = webdriver.get_html(self.url_meta)
        print(f"{self._html_msg}{self.url_meta}")

        soup = bs4.BeautifulSoup(html, "html.parser")
        films = [
            td for td in soup.find_all("td") if td.find("span", class_="versionc2")
        ]

        for film in films:
            try:
                meta_info_show = self._extract_meta_info_show(film)
                meta_info_program[meta_info_show.title] = meta_info_show
            except Exception:
                continue
        return meta_info_program

    def _extract_meta_info_show(self, film: bs4.BeautifulSoup) -> MetaInfo:
        duration = re.search(r"Länge:\s\d+\sMin", film.text)[0]
        description = film.find_all("br")[-1].next_sibling.replace("\n", "").strip()
        return MetaInfo(
            title=film.find("span", class_="versionc2").text.strip(),
            description=duration + ". " + description,
            country=film.find("br").previous_sibling.strip(),
        )

    def _adjust_show(self, show, meta_info):
        """
        Use the information in metainfo to update all the shows in program
        """
        show.dubbed = dubbed.is_dubbed(show, meta_info)
        show.description = meta_info.description
        show.description_start = show_defaults.make_description_start(show.description)
        show.description_end = show_defaults.make_description_end(
            show.description, show.description_start
        )
        show.url_info = meta_info.url_info
        return show


class Schauburg(Filmkunst):
    def __init__(self):
        super().__init__(
            name="Schauburg",
            url="http://www.bremerfilmkunsttheater.de/Kino_Reservierungen/Schauburg.html",
            url_program="https://www.kinoheld.de/kino-bremen/schauburg-kino-bremen/shows/shows?mode=widget",
            # url_meta="https://www.kinoheld.de/kino-bremen/schauburg-kino-bremen/shows/movies?mode=widget",
            url_meta="http://www.bremerfilmkunsttheater.de/site/aktuell.html",
        )


class Gondel(Filmkunst):
    def __init__(self):
        super().__init__(
            name="Gondel",
            url="http://www.bremerfilmkunsttheater.de/Kino_Reservierungen/Gondel.html",
            url_program="https://www.kinoheld.de/kino-bremen/gondel-filmtheater-bremen/shows/shows?mode=widget",
            # url_meta="https://www.kinoheld.de/kino-bremen/gondel-filmtheater-bremen/shows/movies?mode=widget",
            url_meta="http://www.bremerfilmkunsttheater.de/site/aktuell.html",
        )


class Atlantis(Filmkunst):
    def __init__(self):
        super().__init__(
            name="Atlantis",
            url="http://www.bremerfilmkunsttheater.de/Kino_Reservierungen/Atlantis.html",
            url_program="https://www.kinoheld.de/kino-bremen/atlantis-filmtheater-bremen/shows/shows?mode=widget",
            # url_meta="https://www.kinoheld.de/kino-bremen/atlantis-filmtheater-bremen/shows/movies?mode=widget",
            url_meta="http://www.bremerfilmkunsttheater.de/site/aktuell.html",
        )


if __name__ == "__main__":
    schauburg = Schauburg()
    # schauburg._update_meta_info()
    schauburg.update_program(start_driver=True)
    print(schauburg.program)
    print(schauburg._meta_info)
    print(schauburg.program[0])

# IN CASE THEY START USING KINOHELD AGAIN
#     def _update_meta_info(self):
#         print(f"\n updating meta info {self.name}")
#         button_classes = [
#             "ui-button.ui-corners-bottom-left.ui-ripple.ui-button--secondary.u-flex-grow-1",
#             "ui-button.ui-corners-bottom.ui-ripple.ui-button--secondary.u-flex-grow-1",
#         ]
#         try:
#             html = webdriver.get_html_buttons(self.url_meta, button_classes)
#             print(f"{self._html_msg}{self.url_meta}")
#             self.meta_info = _extract_meta_info(html)
#         except Exception as e:
#             statement = f"Note! Meta info from {self.name} was not updated because of an error. {e}"
#             print(statement)
#
#     def _adjust_show(self, show, meta_info):
#         """
#         Use the information in metainfo to update all the shows in program
#         """
#         show.dubbed = dubbed.is_dubbed(show, meta_info)
#         show.description = meta_info.description
#         return show
#
#
# def _extract_meta_info(html):
#     """
#     note: metainfo["country"] is lazily the first 100 characters of description.
#
#     Parameters
#     ----------
#     html: str
#         html source containing the meta info
#
#     Returns
#     -------
#     dict
#         a dict that maps titles to MetaInfo()
#     """
#
#     meta_info = {}
#     soup = bs4.BeautifulSoup(html, "html.parser")
#     films = soup.find_all("article")
#     for film in films:
#         try:
#             stats = _get_stats(film)
#             description = film.find("div", class_="movie__info-description").text
#             title = stats["titel"]
#         except AttributeError:  # in case there is not enough information for the meta database, such as no <dd>
#             continue
#
#         country = description[0:100]
#         meta_info[title] = MetaInfo(
#             title=title,
#             title_original=stats.get("originaltitel"),
#             description=stats.get("dauer") + " " + description,
#             country=country,
#         )
#     return meta_info
#
#
# def _get_stats(film: Tag) -> dict:
#     dls = film.find_all("dl")
#     dt = [t.text.strip().lower() for t in parsing.list_nested_tag(dls, "dt")]
#     dd = [t.text.strip() for t in parsing.list_nested_tag(dls, "dd")]
#     return dict(zip(dt, dd))
