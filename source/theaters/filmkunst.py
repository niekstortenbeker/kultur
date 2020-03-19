import bs4
from helper import webdriver, parsing
from program.metainfo import MetaInfo
from theaters.kinoheld import Kinoheld


class Filmkunst(Kinoheld):
    """Theaters from Filmkunst (Schauburg, Gondel, Atlantis)

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

    def __init__(self, name, url, url_program, url_meta):
        """
        Parameters
        ----------
        name : str
            the name of the theater
        url : str
            url to the homepage of the theater
        url_program: str
            url to the program used for scraping the program
        url_meta: str
            url used for scraping the meta info
        """

        super().__init__(name, url, url_program=url_program, url_meta=url_meta)

    def _update_meta_info(self):
        """
        update self.meta_info by web scraping
        """

        print(f"\n updating meta info {self.name}")
        button_classes = [
            "ui-button.ui-corners-bottom-left.ui-ripple.ui-button--secondary.u-flex-grow-1",
            "ui-button.ui-corners-bottom.ui-ripple.ui-button--secondary.u-flex-grow-1",
        ]
        overlay_class = "overlay-container"
        try:
            html = webdriver.get_html_buttons(self.url_meta, button_classes, overlay_class)
            print(f"{self._html_msg}{self.url_meta}")
            meta = self._extract_meta(html)
            self.meta_info = MetaInfo(meta)
        except Exception as e:
            statement = f"Note! Meta info from {self.name} was not updated because of an error. {e}"
            print(statement)

    def _extract_meta(self, html):
        """
        update self.meta_info by web scraping

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
                dls = film.find_all("dl")
                dt = [t.text.strip().lower() for t in parsing.list_nested_tag(dls, "dt")]
                dd = [t.text.strip() for t in parsing.list_nested_tag(dls, "dd")]
                description = film.find("div", class_="movie__info-description").text
                meta_film = {"title": dd[dt.index("titel")],
                             "description": description,
                             }
            except AttributeError:  # in case there is not enough information for the meta database, such as no <dd>
                continue
            meta_film["country"] = meta_film["description"][0:100]
            if "dauer" in dt:
                meta_film["duration"] = dd[dt.index("dauer")]
            if "genre" in dt:
                meta_film["genre"] = dd[dt.index("genre")]
            if "originaltitel" in dt:
                meta_film["title_original"] = dd[dt.index("originaltitel")]
            if "erscheinungsdatum" in dt:
                meta_film["year"] = dd[dt.index("erscheinungsdatum")][-4:]
            img_screenshot = film.find("div", class_="movie__scenes")
            if img_screenshot:
                img_screenshot = img_screenshot.find_all("img")
                meta_film["img_screenshot"] = [
                    img.get("data-src").strip() for img in img_screenshot
                ]
            img_poster = film.find("div", class_="movie__image")
            if img_poster:
                img_poster = img_poster.find("img").get("src").strip()
                meta_film["img_poster"] = f"{img_poster}"
            meta_info[meta_film["title"]] = meta_film
        return meta_info


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