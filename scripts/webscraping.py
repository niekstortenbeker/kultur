import bs4
import requests
import sys
import arrow
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.firefox.options import Options


def start_driver():
    global driver
    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference("intl.accept_languages", 'de')
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options, firefox_profile=firefox_profile)


def close_driver():
    driver.quit()


class CombinedProgram:

    def __init__(self):
        """theaters should be Theater objects, program should be a Program object"""
        schauburg = Kinoheld(name='Schauburg',
                             url_program_info='http://www.bremerfilmkunsttheater.de/Kino_Reservierungen/Schauburg.html',
                             url_program_scrape='https://www.kinoheld.de/kino-bremen/schauburg-kino-bremen/shows/shows?mode=widget',
                             url_meta='https://www.kinoheld.de/kino-bremen/schauburg-kino-bremen/shows/movies?mode=widget')
        gondel = Kinoheld(name='Gondel',
                          url_program_info='http://www.bremerfilmkunsttheater.de/Kino_Reservierungen/Gondel.html',
                          url_program_scrape='https://www.kinoheld.de/kino-bremen/gondel-filmtheater-bremen/shows/shows?mode=widget',
                          url_meta='https://www.kinoheld.de/kino-bremen/gondel-filmtheater-bremen/shows/movies?mode=widget')
        atlantis = Kinoheld(name='Atlantis',
                            url_program_info='http://www.bremerfilmkunsttheater.de/Kino_Reservierungen/Atlantis.html',
                            url_program_scrape='https://www.kinoheld.de/kino-bremen/atlantis-filmtheater-bremen/shows/shows?mode=widget',
                            url_meta='https://www.kinoheld.de/kino-bremen/atlantis-filmtheater-bremen/shows/movies?mode=widget')
        cinema_ostertor = CinemaOstertor()
        # city_46 = City46()
        # theater_bremen = TheaterBremen()
        # schwankhalle = Schwankhalle()
        # glocke = Glocke()
        # kukoon = Kukoon()
        self.theaters = [
            schauburg,
            gondel,
            atlantis,
            cinema_ostertor,
            # city_46,
            # theater_bremen,
            # schwankhalle,
            # glocke,
            # kukoon
        ]
        self.program = Program(None)

    def update_program(self):
        """
update the complete program

The program is updated both in the theater.program of self.theaters,
and in self.program.
        """
        # update program
        start_driver()
        for t in self.theaters:
            t.update_program()
        # update meta info
        meta_theaters = ['Schauburg', 'Gondel', 'Atlantis', 'Cinema Ostertor']
        for t in self.theaters:
            if t.name in meta_theaters:
                t.update_meta_info()
        close_driver()
        self.refresh_program()

    def refresh_program(self):
        """make a new self.program based on the programs in self.theaters"""
        self.program.empty()
        for t in self.theaters:
            self.program = self.program + t.program
        self.program.sort()


class Program():
    """should be initialized with either shows: a list of Show objects, or
    a list of ShowMetaInfo objects, or with None"""

    def __init__(self, shows):
        """shows should be a list of Show objects or None"""
        super().__init__()
        if shows is None:
            self.shows = []
        else:
            self.shows = shows

    def __repr__(self):
        return f'Program({self.shows})'

    def __add__(self, other):
        shows = self.shows + other.shows
        return Program(shows)

    def empty(self):
        self.shows = []

    def sort(self):
        if isinstance(self.shows[0], Show):
            self.shows.sort(key=lambda show: show.date_time)
        elif isinstance(self.shows[0], ShowMetaInfo):
            self.shows.sort(key=lambda show: show.title)

    def get_next_week(self):
        # TODO
        pass

    def get_day(self):
        # TODO
        pass

    def sort_name(self):
        # TODO
        pass


class Show:
    """TODO explain what this object is. A date_time is always required"""

    def __init__(self,
                 date_time,
                 title='',
                 artist='',
                 link_info='',
                 link_tickets='',
                 location_details='',
                 location='',
                 info='',
                 price='',
                 language_version=''
                 ):
        self.date_time = date_time
        self.title = title
        self.artist = artist
        self.link_info = link_info
        self.link_tickets = link_tickets
        self.location_details = location_details
        self.location = location
        self.info = info
        self.price = price
        self.language_version = language_version

    def __repr__(self):
        d = self.date_time
        date_time = f'{d.month:02d}-{d.day:02d} {d.hour:02d}:{d.minute:02d}'
        return f'Show({date_time}, {self.title}, {self.location})'

    def display(self):
        # TODO
        pass


class ShowMetaInfo:

    def __init__(self,
                 title,
                 title_original='',
                 country='',
                 year='',
                 genre='',
                 duration='',
                 director='',
                 language='',
                 description='',
                 img_poster='',
                 img_screenshot='',
                 link_info='',
                 ):
        self.title = title
        self.title_original = title_original
        self.country = country
        self.year = year
        self.genre = genre
        self.duration = duration
        self.director = director
        self.language = language
        self.description = description
        self.img_poster = img_poster
        self.img_screenshot = img_screenshot
        self.link_info = link_info

    def __repr__(self):
        return f'ShowMetaInfo({self.title})'


# TODO maybe explain that this class is only meant to inherit from
class Theater:
    def __init__(self, name, url, program=None, meta_info=None):
        """program should be a Program object, meta info a dict title as keys and ShowMetaInfo objects as values"""
        self.name = name
        self.url = url
        self.program = program
        self.meta_info = meta_info

    def __repr__(self):
        return f'Theater({self.name})'

    def _get_html_from_web(self, url):
        print('    ...loading webpage (requests)')
        try:
            response = requests.get(url)
            if response.status_code == 404:
                print('    tried but failed to retrieve html from: ', url)
                return None
            else:
                print('    Retrieved html from: ', url)
                return response.text
        except requests.exceptions.ConnectionError as e:
            print("    Error! Connection error: {}".format(e))
            print('    the script is aborted')
            sys.exit(1)

    def _get_html_from_web_ajax(self, url, class_name):
        """Get page source code from a web page that uses ajax to load elements of the page one at a time.
         Selenium will wait for the element with the class name 'class_name' to load before getting the page source"""
        print('    ...loading webpage (selenium)')
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))
            source = driver.page_source
        except TimeoutException:
            print("    Error! Selenium Timeout: {}".format(url))
            print('    tried but failed to retrieve html from: ', url)
            return None
        except WebDriverException as e:
            print("    Error! Selenium Exception. {}".format(str(e)))
            print('    tried but failed to retrieve html from: ', url)
            return None
        print('    Retrieved html from: ', url)
        return source

    def _parse_date_without_year(self, month, day, hour, minute):
        """get arrow object, guess the year. Assumes that dates don't go back more than 2 months.
        Useful when year is not available"""
        year = arrow.now('Europe/Berlin').year  # get current year
        date_time = arrow.get(year, month, day, hour, minute, tzinfo="Europe/Berlin")
        if date_time < arrow.now("Europe/Berlin").shift(months=-2):
            return date_time.replace(year=date_time.year + 1)
        else:
            return date_time

    def find_and_change_case_errors(self):
        """for the shows in db_programinfo with no entry in db_metainfo, see if these no matches can be resolved when
        ignoring case. If so, change case of the title db_metainfo to reflect the case in db_programinfo"""
        print(f'\n  finding case errors in show names of {self.name}')
        program_titles = set([s.title for s in self.program])
        meta_titles = set([s.title for s in self.meta_info])
        no_matches = program_titles - meta_titles
        if no_matches:
            matches_after_case_change = []
            # TODO make this more obvious
            for no_match in no_matches:
                for meta_title in meta_titles:
                    if no_match.lower() == meta_title.lower():
                        self.adjust_name(matches_after_case_change, meta_title, no_match)
                    elif self.alphanumeric(no_match) == self.alphanumeric(meta_title):
                        self.adjust_name(matches_after_case_change, meta_title, no_match)

            no_matches_after_case_change = no_matches - set(matches_after_case_change)

            for title in no_matches_after_case_change:
                print(f'    no meta data found for the show "{title}" in {self.name}')
        else:
            print("    lookin' good!")

    def adjust_name(self,  matches_after_case_change, meta_title, no_match):
        # TODO make this work
        matches_after_case_change.append(no_match)
        metainfo = db_metainfo[location].pop(meta_title)
        db_metainfo[location][no_match] = metainfo
        print(f'    adjusted show title "{meta_title}" to "{no_match}" in db_metainfo')

    def alphanumeric(self, s):
        """convert all adjecent non-alphanumeric characters to a single space, and makes lowercase"""
        s = s.lower()
        # TODO this would ignore german umlaud etc
        return re.sub('[^0-9a-zA-Z]+', ' ', s)


class Kinoheld(Theater):

    def __init__(self, name, url_program_info, url_program_scrape, url_meta):
        super().__init__(name, url_program_info)
        self.url_program_scrape = url_program_scrape
        self.url_meta = url_meta

    def update_program(self):
        print(f'\n updating program {self.name}')
        html = self._get_html_from_web_ajax(self.url_program_scrape, 'movie.u-px-2.u-py-2')
        try:
            show_list = self._extract_show_list(html)
            self.program = Program(show_list)
            self.program.sort()
        except (TypeError, AttributeError, ValueError):
            print(f"Note! Program from {self.name} was not updated because of an error")


    def _extract_show_list(self, html):
        show_list = []
        soup = bs4.BeautifulSoup(html, 'html.parser')
        shows = soup.find_all('article')
        for s in shows:
            show = Show(self._get_date_time(s))
            if self.name == 'Cinema Ostertor':
                show.title = self._get_title(s).title()
            else:
                show.title = self._get_title(s)
            show.language_version = self._get_language_version(s)
            show.link_tickets = 'https://www.kinoheld.de/' + s.a.get('href')
            show.link_info = self.url
            show.location = self.name
            show_list.append(show)
        return show_list

    def _get_language_version(self, film):
        if film.find(class_='movie__title').span:
            language_version = film.find(class_='movie__title').span.text.strip()
        else:
            language_version = ''
        return language_version

    def _get_date_time(self, film):
        date_time = film.find(class_='movie__date').text
        month = int(date_time[6:8])
        day = int(date_time[3:5])
        hour = int(date_time[10:12])
        minute = int(date_time[13:15])
        return self._parse_date_without_year(month, day, hour, minute)

    def _get_title(self, film):
        """get title from film. do some cleaning to remove white lines from some titles (OmeU and OmDU are shortened)"""
        title = film.find(class_='movie__title').text.strip()
        if title[-3:] in ['OmU', ' OV', 'mdU', 'meU']:
            title = title[:-3].strip()
        return title

    def update_meta_info(self):
        print(f'\n updating meta info {self.name}')
        html = self._get_meta_html(self.url_meta)
        try:
            meta = self._extract_meta(html)
            self.meta_info = Program(meta)
        except (TypeError, AttributeError, ValueError):
            print(f"Note! Meta info from {self.name} was not updated because of an error")

    def _get_meta_html(self, url):
        """I need to click some buttons to get all the info in the html. It should wait for the overlay to be gone."""
        print('    ...loading webpage meta kinoheld (selenium)')
        driver.get(url)
        self._wait_for_overlay()
        source = self._click_buttons(url)
        return source

    def _click_buttons(self, url):
        """click two button types: one if there is also a trailer, one if there is only info without a trailer"""
        buttons = self._get_buttons()
        while not buttons:  # sometimes this still needs more time
            time.sleep(1)
            buttons = self._get_buttons()
        clicking = self._try_clicking(buttons[0])
        while not clicking:  # sometimes there are still overlay classes preventing clicking
            time.sleep(1)
            clicking = self._try_clicking(buttons[0])
        del buttons[0]
        for button in buttons:
            button.click()
        source = driver.page_source
        print('    Retrieved html from: ', url)
        return source

    def _get_buttons(self):
        button_classes = ['ui-button.ui-corners-bottom-left.ui-ripple.ui-button--secondary.u-flex-grow-1',
                          'ui-button.ui-corners-bottom.ui-ripple.ui-button--secondary.u-flex-grow-1']
        buttons = driver.find_elements_by_class_name(button_classes[0])
        buttons.extend(driver.find_elements_by_class_name(button_classes[1]))
        if buttons:
            return buttons
        else:
            return None

    def _wait_for_overlay(self):
        try:
            wait = WebDriverWait(driver, 10)
            overlay_class = "overlay-container"
            wait.until_not(EC.visibility_of_element_located((By.CLASS_NAME, overlay_class)))
            return True
        except WebDriverException:
            return False

    def _try_clicking(self, button):
        try:
            button.click()
            return True
        except ElementClickInterceptedException:
            return False

    def _extract_meta(self, html):
        meta_info = []
        soup = bs4.BeautifulSoup(html, 'html.parser')
        films = soup.find_all('article')
        # TODO: organize this more like in cinema ostertor. I think I'm missing a lot
        for film in films:
            try:
                dl = film.find(class_='movie__additional-data').find('dl')
                dt = [tag.text.strip().lower() for tag in dl.find_all('dt')]
                dd = [tag.text.strip() for tag in dl.find_all('dd')]
                meta_film = ShowMetaInfo(dd[dt.index('titel')])
                if 'originaltitel' in dt:
                    meta_film.title_original = dd[dt.index('originaltitel')]
                if 'produktion' in dt:
                    meta_film.country = dd[dt.index('produktion')][:-4].strip().rstrip(',')
                if 'erscheinungsdatum' in dt:
                    meta_film.year = dd[dt.index('erscheinungsdatum')][-4:]
                if 'regie' in dt:
                    meta_film.director = dd[dt.index('regie')]
                if 'darsteller' in dt:
                    meta_film.actors = dd[dt.index('darsteller')]
                meta_film.description = ''.join([p.text for p in film.find_all('p')])
                img_screenshot = film.find('div', class_='movie__scenes')
                if img_screenshot:
                    img_screenshot = img_screenshot.find_all('img')
                    meta_film.img_screenshot = [img.get('data-src').strip() for img in img_screenshot]
                img_poster = film.find('div', class_='movie__image')
                if img_poster:
                    img_poster = img_poster.find('img').get('src').strip()
                    meta_film.img_poster = f'https://www.kinoheld.de{img_poster}'

                meta_info.append(meta_film)

            except AttributeError:  # in case there is not enough information for the meta database, such as no <dd>
                pass
        return meta_info


class CinemaOstertor(Kinoheld):
    # TODO use url from meta info for program_link

    def __init__(self):
        url = 'https://cinema-ostertor.de/aktuelle-filme'
        super().__init__(name='Cinema Ostertor',
                         url_program_info=url,
                         url_program_scrape='https://www.kinoheld.de/kino-bremen/cinema-im-ostertor-bremen/shows/shows?mode=widget',
                         url_meta=url)

    def update_meta_info(self):
        print(f'\n updating meta info {self.name}')
        try:
            urls = self._get_meta_urls()
            meta = self._extract_meta(urls)
            self.meta_info = Program(meta)
        except (TypeError, AttributeError, ValueError):
            print(f"Note! meta info from {self.name} was not updated because of an error")

    def _get_meta_urls(self):
        html = self._get_html_from_web(self.url_meta)
        soup = bs4.BeautifulSoup(html, 'html.parser')
        urls = [url.get('href').strip() for url in soup.find_all('a', class_='details')]
        return urls

    def _extract_meta(self, movie_urls):
        # TODO: film info is actually spread over two pages, right now only gets first page
        meta_info_program = []
        for url in movie_urls:
            html = self._get_html_from_web(url)
            try:
                meta_info_show = self._parse_show(html)
                meta_info_program.append(meta_info_show)
            except TypeError:
                print(f"No meta info was extracted because of a NoneType (url: {url})")
        return {self.name: meta_info_program}

    def _parse_show(self, html):
        """from a html page with supposedly film info extract meta info in a ShowMetaInfo object.
        Return the title and the object. Should return a None if it doesn't work"""
        soup = bs4.BeautifulSoup(html, 'html.parser')
        # many stats are hidden in a sloppy bit of html in h6
        # in case there is a web page that doesn't display a normal film have this bit in a try except block
        try:
            stats = soup.find('h6')
            d = {}
            for strong in stats.find_all('strong'):
                name = strong.previous_sibling.strip().lower()
                description = strong.text.strip()
                d[name] = description
        except AttributeError:
            return None
        translate = {
            'title_original': 'originaler titel:',
            'country': 'produktion:',
            'year': 'erscheinungsdatum:',
            'genre': 'genre:',
            'duration': 'dauer:',
            'director': 'regie:',
        }
        try:
            meta_film = ShowMetaInfo(d['titel:'])
        except KeyError:  # If I can't parse the title I don't want anything
            return None
        for key in translate.keys():
            try:
                meta_film.key = d[translate[key]]
            except KeyError:
                continue
        # do some necessary cleaning
        if meta_film.year:
            meta_film.year = meta_film.year[-4:]
        if meta_film.duration:
            meta_film.duration = meta_film.duration.replace('\xa0', ' ')
        # get other data
        img_screenshot = soup.find('img', class_='rev-slidebg')
        if img_screenshot:
            meta_film.img_screenshot = img_screenshot.get('src').strip()
        meta_film.img_poster = soup.find('img', class_='vc_single_image-img').get('src').strip()
        meta_film.description = soup.find('p').text
        return meta_film


class City46(Theater):

    def __init__(self):
        super().__init__('City 46', 'http://www.city46.de/programm/')

    def update_program(self):
        # TODO maybe use pandas pd.read_html(str(soup.find('table')))[0]
        print(f'\n updating program {self.name}')
        show_list = []
        urls, years = self._get_urls()
        try:
            for url, year in zip(urls, years):
                html = self._get_html_from_web(url)
                table = self._get_tables_from_html(html)
                show_list.extend(self._extract_show_list(table, year))
            self.program = Program(show_list)
            self.program.sort()
        except (TypeError, AttributeError, ValueError):
            print(f"Note! Program from {self.name} was not updated because of an error")

    def _get_urls(self):
        """use today's date to figure out the city 46 program url. If date > 20 also get next month"""
        urls, years = [], []
        months = {1: 'januar', 2: 'februar', 3: 'maerz', 4: 'april', 5: 'mai', 6: 'juni', 7: 'juli', 8: 'august',
                  9: 'september', 10: 'oktober', 11: 'november', 12: 'dezember'}
        date = arrow.now('Europe/Berlin')
        year, month, day = date.year, date.month, date.day
        urls.append("{}{}-{}.html".format(self.url, months[month], year))
        years.append(year)
        if day > 20:
            date = date.shift(months=+1)
            year, month = date.year, date.month
            urls.append("{}{}-{}.html".format(self.url, months[month], year))
            years.append(year)
        return urls, years

    def _get_tables_from_html(self, html):
        """Parses all tables from a website. The tables are merged and are saved as a list of
        lists, in which the inner lists are the rows. The cells are stored as bs4.element.Tag.
        Note, it does not handle rowspan or colspan"""
        soup = bs4.BeautifulSoup(html, 'html.parser')

        table = []
        for row in soup.find_all('tr'):  # <tr> = row
            row_list = [cell for cell in row.find_all(['td', 'th'])]  # <td> = data cell <th> = header cell
            table.append(row_list)
        return table

    def _clean_rowspan_in_table(self, html_table):
        """ adjust the layout of and html_table if rowspan is used to still include the cells in the row below.
        Note that if you would display this in HTML it would have extra cells"""
        rowspans = {}

        for row in html_table:
            # first insert empty cells if rowspan was defined
            if rowspans:
                for column_number in rowspans:
                    if rowspans[column_number] > 1:
                        row.insert(column_number, bs4.BeautifulSoup('<td></td>', 'html.parser'))
                        rowspans[column_number] -= 1
            # then look for new rowspans in the row
            for row_number, cell in enumerate(row):
                if cell.has_attr('rowspan'):
                    rowspans[row_number] = int(cell['rowspan'])
        return html_table

    def _extract_show_list(self, html_table, year):
        """ very ugly this, but the HTML is also really ugly.
        save film info in a temporary dictionary that changes throughout the for loop through the table.
        In this for loop the dictionary is saved as a ProgramInfo namedtuple, which is appended to a list. This dictionary
        is exported +/- every time when the loop encounters a time (indicating a new film)"""
        show_list = []
        temp_dict = {'date': None, 'time': None, 'link': None, 'title': None, 'info': None}
        re_date = re.compile(r"\d{1,2}\.\d{1,2}\.?")  # last .? in case they forget last dot
        re_time = re.compile(r"\d\d:\d\d")

        for row in html_table:
            for cell in row:
                if cell.text:
                    if cell.text in ['MO', 'DI', 'MI', 'DO', 'FR', 'SA', 'SO']:
                        if temp_dict['date'] and temp_dict['title'] and temp_dict['time']:
                            show_list.append(
                                self._save_show(temp_dict, year))  # 1/3 save the last film of the previous day
                        temp_dict = dict.fromkeys(temp_dict, None)  # remove all values
                    elif re_date.match(cell.text):
                        temp_dict['date'] = self._add_dot_to_date(cell.text)
                    elif re_time.match(cell.text):
                        if temp_dict['date'] and temp_dict['title'] and temp_dict['time']:
                            show_list.append(self._save_show(temp_dict, year))  # 2/3 save all other films
                        temp_dict['time'] = cell.text.strip()
                    elif cell.find('a'):
                        temp_dict['link'] = 'http://www.city46.de/' + cell.find('a').get('href')
                        title = cell.find('a').text
                        temp_dict['title'] = title
                        temp_dict['info'] = cell.text[len(title):]  # separate the title from the other info
                    else:  # in case there is extra info in the most right column
                        if temp_dict['info']:  # this was once necessary
                            temp_dict['info'] = temp_dict['info'] + ' | ' + cell.text
        if temp_dict['date'] and temp_dict['title'] and temp_dict['time']:
            show_list.append(self._save_show(temp_dict, year))  # 3/3 save the last movie of the month
        return show_list

    def _add_dot_to_date(self, string):
        """in case they forgot the last dot in the date, add this dot"""
        if string[-1] == '.':
            return string.strip()
        elif string[-1] != '.':
            string = string + '.'
            return string.strip()

    def _save_show(self, temp_dict, year):
        date_time = arrow.get(temp_dict['date'] + temp_dict['time'], 'D.M.hh:mm', tzinfo='Europe/Berlin')
        show = Show(date_time.replace(year=year))
        show.title = temp_dict['title']
        show.link_info = temp_dict['link']
        show.info = temp_dict['info']
        show.location = self.name
        return show


class TheaterBremen(Theater):
    def __init__(self):
        super().__init__('Theater Bremen', 'http://www.theaterbremen.de')

    def update_program(self):
        print(f'\n updating program {self.name}')
        show_list = []
        urls = self._get_urls()
        try:
            for url in urls:
                html = self._get_html_from_web_ajax(url, class_name='day')
                show_list.extend(self._extract_show_list(html))
            self.program = Program(show_list)
            self.program.sort()
        except (TypeError, AttributeError, ValueError):
            print(f"Note! Program from {self.name} was not updated because of an error")

    def _get_urls(self):
        """use today's date to figure out the theaterbremen program url. If date > 20 also get next month"""
        urls = []
        date = arrow.now('Europe/Berlin')
        year, month, day = date.year, date.month, date.day
        urls.append("{}#?d={}-{}-{}&f=a".format(self.url, year, month, day))
        if day > 20:
            date = date.shift(months=+1)
            year, month = date.year, date.month
            urls.append("{}#?d={}-{}-{}&f=a".format(self.url, year, month, 20))
        return urls

    def _extract_show_list(self, html):
        show_list = []
        soup = bs4.BeautifulSoup(html, 'html.parser')
        days = soup.find_all(class_='day')
        for day in days:
            date = day.find(class_='date').text.strip()[-10:]
            shows = day.find_all('article')
            for s in shows:
                time = s.find(class_='overview-date-n-flags').text.strip()[0:5]
                show = Show(arrow.get(date + time, 'DD.MM.YYYYHH:mm', tzinfo='Europe/Berlin'))
                links = s.find_all('a')
                show.link_info = '{}{}'.format(self.url, links[1].get('href').strip())
                try:
                    show.link_tickets = links[2].get('href').strip()
                    show.price = links[2].text.strip()
                except IndexError:
                    pass
                show.title = links[1].text.strip()
                infos = s.find_all('p')
                show.info = '\n'.join(info.text for info in infos)
                show.location = self.name
                show_list.append(show)
        return show_list


class Schwankhalle(Theater):

    def __init__(self):
        super().__init__('Schwankhalle', 'http://schwankhalle.de/spielplan-1.html')

    def update_program(self):
        print(f'\n updating program {self.name}')
        # at some point requests starting giving SSLError so use selenium for ajax
        html = self._get_html_from_web_ajax(self.url, 'date-container')
        try:
            show_list = self._extract_show_list(html)
            self.program = Program(show_list)
            self.program.sort()
        except (TypeError, AttributeError, ValueError):
            print(f"Note! Program from {self.name} was not updated because of an error")

    def _extract_show_list(self, html):
        show_list = []
        soup = bs4.BeautifulSoup(html, 'html.parser')

        year = soup.find("td", class_="year-month").text.strip()[0:4]
        table = soup.find('table')
        for row in table.find_all('tr'):  # normal for row in table did not work
            if isinstance(row, str):  # skip empty table rows
                continue
            if not row.find(class_='time-container'):  # going to assume that a program row always has a time cell
                continue
            if not row.find(class_='date-container'):  # solves nonetype errors
                continue
            show = Show(self._get_date_time(row, year))
            title_artist_info = row.find('td', class_='title')
            artist = title_artist_info.a.span.text
            title = title_artist_info.a.text[len(artist) + 1:]  # title is not separated by tags
            show.info = title_artist_info.text[len(title) + 1:].strip()  # info is not separated by tags
            show.artist = artist.strip()
            show.title = title.strip()
            link = 'https://schwankhalle.de/{}'.format(row.a.get('href').strip())
            show.link_info = link
            show.link_tickets = link
            show.location = self.name
            show_list.append(show)
        return show_list

    def _get_date_time(self, row, year):
        date = row.find(class_='date-container').text.strip()
        date = date + year
        time = row.find(class_='time-container').text.strip()[-9:-4]  # in case the time is 'ab ...'
        if not time:
            time = '09:00'
        date_time = arrow.get(date + time, 'D.M.YYYYhh:mm', tzinfo='Europe/Berlin')
        return date_time


class Glocke(Theater):

    def __init__(self):
        super().__init__('Glocke', 'https://www.glocke.de/')

    def update_program(self):
        print(f'\n updating program {self.name}')
        urls = self._get_urls()
        show_list = []
        try:
            for url in urls:
                html = self._get_html_from_web(url)
                show_list.extend(self._extract_show_list(html))
            self.program = Program(show_list)
            self.program.sort()
        except (TypeError, AttributeError, ValueError):
            print(f"Note! Program from {self.name} was not updated because of an error")

    def _get_urls(self):
        arw = arrow.now()
        url1 = self.url + f'/de/Veranstaltungssuche/{arw.month}/{arw.year}'
        arw = arw.shift(months=+1)
        url2 = self.url + f'/de/Veranstaltungssuche/{arw.month}/{arw.year}'
        urls = [url1, url2]
        return urls

    def _extract_show_list(self, html):
        show_list = []
        soup = bs4.BeautifulSoup(html, 'html.parser')
        shows = soup.find_all('div', class_='va-liste')
        for s in shows:
            date_time, location_details = self._get_date_time_and_location_details(s)
            show = Show(date_time)
            show.location_details = location_details
            show.title = self._get_title(s)
            link = self.url + '{}'.format(s.a.get('href'))
            show.link_info = link
            show.link_tickets = link
            show.location = self.name
            show_list.append(show)
        return show_list

    def _get_title(self, show):
        title = str(show.find('h2')).strip()
        title = title.replace('<h2>', '')
        title = title.replace('</h2>', '')
        title = title.replace('<br/>', ' - ')
        return title

    def _get_date_time_and_location_details(self, show):
        day = int(show.find(class_=re.compile(r"va_liste_datum_1")).text.strip())
        month = show.find(class_=re.compile(r"va_liste_datum_2")).text.strip().lower()
        months = {'jan': 1, 'feb': 2, 'mär': 3, 'maer': 3, 'märz': 3, 'apr': 4, 'mai': 5, 'jun': 6, 'jul': 7,
                  'aug': 8, 'sep': 9, 'sept': 9, 'okt': 10, 'nov': 11, 'dez': 12}
        month = months[month]
        time_location = show.find('span', style=re.compile(r"color")).text.strip()
        hour, minute = int(time_location[:2]), int(time_location[3:6])
        date_time = self._parse_date_without_year(month, day, hour, minute)
        location_details = time_location[10:]
        return date_time, location_details


class Kukoon(Theater):

    def __init__(self):
        super().__init__('Kukoon', 'https://kukoon.de/programm/')

    def update_program(self):
        print(f'\n updating program {self.name}')
        html = self._get_html_from_web(self.url)
        try:
            show_list = self._extract_show_list(html)
            self.program = Program(show_list)
            self.program.sort()
        except (TypeError, AttributeError, ValueError):
            print(f"Note! Program from {self.name} was not updated because of an error")

    def _extract_show_list(self, html):
        show_list = []
        soup = bs4.BeautifulSoup(html, 'html.parser')
        shows = soup.find_all('div', class_='event')
        for s in shows:
            date_time = s.time
            title_link = s.find(class_='event__title').a
            if not date_time:
                continue
            if 'geschlossene gesellschaft' in title_link.text.lower():
                continue

            show = Show(date_time=arrow.get(date_time.get('datetime')))
            show.link_info = title_link.get('href')
            show.title = title_link.text.strip()
            show.location_details = self._get_location_details(s)
            show.info = s.find(class_='event__categories').text.strip()
            show.location = self.name
            show_list.append(show)
        return show_list

    def _get_location_details(self, show):
        location_details = show.find(class_='event__venue').text.strip()
        if location_details == self.name:
            location_details = ''
        return location_details
