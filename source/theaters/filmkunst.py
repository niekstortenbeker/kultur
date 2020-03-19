from typing import Union
import bs4
from helper import webdriver, parsing
from program.metainfo import MetaInfo
from theaters.kinoheld import Kinoheld

Tag = bs4.element.Tag


class Filmkunst(Kinoheld):
    """Theaters from Filmkunst (Schauburg, Gondel, Atlantis)

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
        print(f"\n updating meta info {self.name}")
        button_classes = [
            "ui-button.ui-corners-bottom-left.ui-ripple.ui-button--secondary.u-flex-grow-1",
            "ui-button.ui-corners-bottom.ui-ripple.ui-button--secondary.u-flex-grow-1",
        ]
        overlay_class = "overlay-container"
        try:
            html = webdriver.get_html_buttons(
                self.url_meta, button_classes, overlay_class
            )
            print(f"{self._html_msg}{self.url_meta}")
            meta = _extract_meta_info(html)
            self.meta_info = MetaInfo(meta)
        except Exception as e:
            statement = f"Note! Meta info from {self.name} was not updated because of an error. {e}"
            print(statement)


def _extract_meta_info(html):
    """
    note: metainfo["country"] is lazily the first 100 characters of description.

    Parameters
    ----------
    html: str
        html source containing the meta info

    Returns
    -------
    dict
        A dictionary that can be used as shows attribute of a MetaInfo()
    """

    meta_info = {}
    soup = bs4.BeautifulSoup(html, "html.parser")
    films = soup.find_all("article")
    for film in films:
        try:
            stats = _get_stats(film)
            description = film.find("div", class_="movie__info-description").text
            meta_film = {
                "title": stats['titel'],
                "description": description,
            }
        except AttributeError:  # in case there is not enough information for the meta database, such as no <dd>
            continue

        meta_film["country"] = meta_film["description"][0:100]
        meta_film["duration"] = stats.get("dauer")
        meta_film["genre"] = stats.get("genre")
        meta_film["title_original"] = stats.get("originaltitel")
        meta_film["year"] = _get_year(stats)
        meta_film["img_screenshot"] = _get_img_screenshot(film)
        meta_film["img_poster"] = _get_img_poster(film)

        meta_info[meta_film["title"]] = meta_film
    return meta_info


def _get_stats(film: Tag) -> dict:
    dls = film.find_all("dl")
    dt = [t.text.strip().lower() for t in parsing.list_nested_tag(dls, "dt")]
    dd = [t.text.strip() for t in parsing.list_nested_tag(dls, "dd")]
    return dict(zip(dt, dd))


def _get_img_poster(film: Tag) -> Union[str, None]:
    img_poster = film.find("div", class_="movie__image")
    if img_poster:
        img_poster = img_poster.find("img").get("src").strip()
    return img_poster


def _get_img_screenshot(film: Tag) -> Union[list, None]:
    img_screenshot = film.find("div", class_="movie__scenes")
    if img_screenshot:
        img_screenshot = img_screenshot.find_all("img")
        return [img.get("data-src").strip() for img in img_screenshot]


def _get_year(stats: dict) -> Union[str, None]:
    year = stats.get("erscheinungsdatum")
    if year:
        return year[-4:]


class Schauburg(Filmkunst):
    def __init__(self):
        super().__init__(
            name="Schauburg",
            url="http://www.bremerfilmkunsttheater.de/Kino_Reservierungen/Schauburg.html",
            url_program="https://www.kinoheld.de/kino-bremen/schauburg-kino-bremen/shows/shows?mode=widget",
            url_meta="https://www.kinoheld.de/kino-bremen/schauburg-kino-bremen/shows/movies?mode=widget",
        )


class Gondel(Filmkunst):
    def __init__(self):
        super().__init__(
            name="Gondel",
            url="http://www.bremerfilmkunsttheater.de/Kino_Reservierungen/Gondel.html",
            url_program="https://www.kinoheld.de/kino-bremen/gondel-filmtheater-bremen/shows/shows?mode=widget",
            url_meta="https://www.kinoheld.de/kino-bremen/gondel-filmtheater-bremen/shows/movies?mode=widget",
        )


class Atlantis(Filmkunst):
    def __init__(self):
        super().__init__(
            name="Atlantis",
            url="http://www.bremerfilmkunsttheater.de/Kino_Reservierungen/Atlantis.html",
            url_program="https://www.kinoheld.de/kino-bremen/atlantis-filmtheater-bremen/shows/shows?mode=widget",
            url_meta="https://www.kinoheld.de/kino-bremen/atlantis-filmtheater-bremen/shows/movies?mode=widget",
        )