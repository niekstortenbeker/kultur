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
from copy import copy


# TODO get individual info of everything
# TODO change naming convention all over to follow ostertor
# TODO also store the url with the film info in the meta info, and maybe in the programinfo, for ostertor
# TODO try to use decorators to also log printed info https://realpython.com/primer-on-python-decorators/

def start_driver():
    global driver
    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference("intl.accept_languages", 'de')
    firefox_profile.update_preferences()  # not sure if this is necessary
    driver = webdriver.Firefox(firefox_profile=firefox_profile)


def close_driver():
    driver.quit()


class Webscraper:
    def __init__(self):
        self.meta_film = {'title': '',
                          'title_original': '',
                          'country': '',
                          'year': '',
                          'genre': '',
                          'duration': '',
                          'director': '',
                          'language': '',
                          'description': '',
                          'img_poster': '',
                          'img_screenshot': '',
                          'link_info': '',
                          }  # I want keys to be present also if values are absent
        # TODO: maybe also get programinfo in here

    def __repr__(self):
        # TODO maybe actually use this
        return "some information"

    def get_html_from_web(self, url):
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

    def get_html_from_web_ajax(self, url, class_name):
        """Get page source code from a web page that uses ajax to load elements of the page one at a time.
         Selenium will wait for the element with the class name 'class_name' to load before getting the page source"""
        print('    ...loading webpage (selenium)')
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))
            source = driver.page_source
        except TimeoutException:
            print("    Error! Selenium Timeout: {}".format(url))
            print('    the script is aborted')
            sys.exit(1)
        except WebDriverException as e:
            print("    Error! Selenium Exception. {}".format(str(e)))
            print('    the script is aborted')
            sys.exit(1)
        print('    Retrieved html from: ', url)
        return source

    def german_month_to_int(self, month):
        month = month.lower().strip('.')
        if len(month) in [3, 4]:
            months = {'jan': 1, 'feb': 2, 'mär': 3, 'maer': 3, 'märz': 3, 'apr': 4, 'mai': 5, 'jun': 6, 'jul': 7,
                      'aug': 8, 'sep': 9, 'sept': 9, 'okt': 10, 'nov': 11, 'dez': 12}
            return months[month]
        else:
            months = {'januar': 1, 'februar': 2, 'märz': 3, 'maerz': 3, 'april': 4, 'mai': 5, 'juni': 6, 'juli': 7,
                      'august': 8, 'september': 9, 'oktober': 10, 'november': 11, 'dezember': 12}
            return months[month]

    def parse_datetime(self, month, day, hour, minute):
        """get arrow object, guess the year"""
        datetime = arrow.now('Europe/Berlin')
        datetime = datetime.replace(month=month,
                                    day=day,
                                    hour=hour,
                                    minute=minute,
                                    second=0,
                                    microsecond=0)
        if datetime < arrow.now("Europe/Berlin").shift(months=-1):
            return datetime.replace(year=datetime.year + 1)
        else:
            return datetime


class Kinoheld(Webscraper):

    def extract_program(self, html, location, program_link):
        program = []
        link = 'https://www.kinoheld.de/'
        soup = bs4.BeautifulSoup(html, 'html.parser')
        films = soup.find_all('article')
        for film in films:
            # get time info
            datetime = film.find(class_='movie__date').text
            month = int(datetime[6:8])
            day = int(datetime[3:5])
            hour = int(datetime[10:12])
            minute = int(datetime[13:15])
            datetime = self.parse_datetime(month, day, hour, minute)

            # get other info
            title = film.find(class_='movie__title').text.strip()
            if title[-3:] in ['OmU', ' OV', 'mdU', 'meU']:  # do some cleaning to remove white lines from some titles (OmeU and OmDU are shortened)
                title = title[:-3].strip()
            if film.find(class_='movie__title').span:
                language_version = film.find(class_='movie__title').span.text.strip()
            else:
                language_version = ''
            link_tickets = link + film.a.get('href')
            programinfo = dict(title=title,
                               datetime=datetime,
                               link_info=program_link,
                               link_tickets=link_tickets,
                               location=location,
                               info='',
                               price='',
                               artist='',
                               language_version=language_version)
            program.append(programinfo)
        return program

    def get_meta_html(self, url):
        # TODO do I get all the meta info?
        """I need to click some buttons to get all the info in the html. It should wait for the overlay to be gone."""
        print('    ...loading webpage meta kinoheld (selenium)')
        driver.get(url)
        self.wait_for_overlay()
        source = self.click_buttons(url)
        return source

    def click_buttons(self, url):
        """click two button types: one if there is also a trailer, one if there is only info without a trailer"""
        button_classes = ['ui-button.ui-corners-bottom-left.ui-ripple.ui-button--secondary.u-flex-grow-1',
                          'ui-button.ui-corners-bottom.ui-ripple.ui-button--secondary.u-flex-grow-1']
        buttons = driver.find_elements_by_class_name(button_classes[0])
        buttons.extend(driver.find_elements_by_class_name(button_classes[1]))
        clicking = self.try_clicking(buttons[0])
        while not clicking:  # sometimes there are still overlay classes preventing clicking
            time.sleep(3)
            clicking = self.try_clicking(buttons[0])
        del buttons[0]
        for button in buttons:
            button.click()
        source = driver.page_source
        print('    Retrieved html from: ', url)
        return source

    def wait_for_overlay(self):
        try:
            wait = WebDriverWait(driver, 10)
            overlay_class = "overlay-container"
            wait.until_not(EC.visibility_of_element_located((By.CLASS_NAME, overlay_class)))
            return True
        except WebDriverException:
            return False

    def try_clicking(self, button):
        try:
            button.click()
            return True
        except ElementClickInterceptedException:
            return False

    def extract_meta(self, html):
        meta_info = {}
        soup = bs4.BeautifulSoup(html, 'html.parser')
        films = soup.find_all('article')

        for film in films:
            try:
                dl = film.find(class_='movie__additional-data').find('dl')
                dt = [tag.text.strip().lower() for tag in dl.find_all('dt')]
                dd = [tag.text.strip() for tag in dl.find_all('dd')]
                meta_film = copy(self.meta_film)
                self.meta_film['title'] = dd[dt.index('titel')]  # I always need a title
                if 'originaltitel' in dt:
                    meta_film['title_original'] = dd[dt.index('originaltitel')]
                if 'produktion' in dt:
                    meta_film['country'] = dd[dt.index('produktion')][:-4].strip().rstrip(',')
                if 'erscheinungsdatum' in dt:
                    meta_film['year'] = dd[dt.index('erscheinungsdatum')][-4:]
                if 'regie' in dt:
                    meta_film['director'] = dd[dt.index('regie')]
                if 'darsteller' in dt:
                    meta_film['actors'] = dd[dt.index('darsteller')]
                meta_film['description'] = ''.join([p.text for p in film.find_all('p')])
                img_screenshot = film.find('div', class_='movie__scenes')
                if img_screenshot:
                    img_screenshot = img_screenshot.find_all('img')
                    meta_film['img_screenshot'] = [img.get('data-src').strip() for img in img_screenshot]
                img_poster = film.find('div', class_='movie__image')
                if img_poster:
                    img_poster = img_poster.find('img').get('src').strip()
                    meta_film['img_poster'] = f'https://www.kinoheld.de{img_poster}'

                meta_info[meta_film['title']] = meta_film

            except AttributeError:  # in case there is not enough information for the meta database, such as no <dd>
                pass
        return meta_info


class Filmkunst(Kinoheld):

    def create_program_db(self):
        complete_program = []

        urls_scrape = ['https://www.kinoheld.de/kino-bremen/schauburg-kino-bremen/shows/shows?mode=widget',
                       'https://www.kinoheld.de/kino-bremen/gondel-filmtheater-bremen/shows/shows?mode=widget',
                       'https://www.kinoheld.de/kino-bremen/atlantis-filmtheater-bremen/shows/shows?mode=widget']
        urls_info = ['http://www.bremerfilmkunsttheater.de/Kino_Reservierungen/Schauburg.html',
                     'http://www.bremerfilmkunsttheater.de/Kino_Reservierungen/Gondel.html',
                     'http://www.bremerfilmkunsttheater.de/Kino_Reservierungen/Atlantis.html']
        names = ['Schauburg', 'Gondel', 'Atlantis']

        for url_scrape, url_info, name in zip(urls_scrape, urls_info, names):
            html = self.get_html_from_web_ajax(url_scrape, 'movie.u-px-2.u-py-2')
            program = self.extract_program(html, name, url_info)
            if not program:
                print(f'!Note, no program could be retrieved from {name} ({url_scrape})')
            complete_program.extend(program)
        return complete_program

    def create_meta_db(self):
        meta_db = {}
        urls = ['https://www.kinoheld.de/kino-bremen/schauburg-kino-bremen/shows/movies?mode=widget',
                'https://www.kinoheld.de/kino-bremen/gondel-filmtheater-bremen/shows/movies?mode=widget',
                'https://www.kinoheld.de/kino-bremen/atlantis-filmtheater-bremen/shows/movies?mode=widget']
        names = ['Schauburg', 'Gondel', 'Atlantis']
        for url, name in zip(urls, names):
            html = self.get_meta_html(url)
            meta = self.extract_meta(html)
            meta_db[name] = meta
        return meta_db


class CinemaOstertor(Kinoheld):
#TODO do I store the language info that is in the kinoheld info?

    def create_program_db(self):
        url = 'https://www.kinoheld.de/kino-bremen/cinema-im-ostertor-bremen/shows/shows?mode=widget'
        html = self.get_html_from_web_ajax(url, 'movie.u-px-2.u-py-2')
        program = self.extract_program(html, location='Cinema Ostertor', program_link='')
        if not program:
            print(f'!Note, no program could be retrieved from Cinema Ostertor ({url})')
        return program

    def create_meta_db(self):
        url = 'https://cinema-ostertor.de/aktuelle-filme'
        movie_urls = self.get_meta_urls(url)
        meta = self.extract_meta(movie_urls)
        return meta

    def get_meta_urls(self, start_url):
        html = self.get_html_from_web(start_url)
        soup = bs4.BeautifulSoup(html, 'html.parser')
        urls = [url.get('href').strip() for url in soup.find_all('a', class_='details')]
        return urls

    def extract_meta(self, movie_urls):
        meta_info_program = {}
        for url in movie_urls:
            html = self.get_html_from_web(url)
            try:
                title, meta_info_show = self.parse_show(html)
                meta_info_program[title] = meta_info_show
            except TypeError:
                print(f"No meta info was extracted because of a NoneType (url: {url})")
        return {'Cinema Ostertor': meta_info_program}

    def parse_show(self, html):
        # TODO should this maybe be more modular still?
        soup = bs4.BeautifulSoup(html, 'html.parser')
        # many stats are hidden in a sloppy bit of html in h6
        stats = soup.find('h6')
        d = {}
        for strong in stats.find_all('strong'):
            name = strong.previous_sibling.strip().lower()
            description = strong.text.strip()
            d[name] = description
        translate = {'title': 'titel:',
                     'title_original': 'originaler titel:',
                     'country': 'produktion:',
                     'year': 'erscheinungsdatum:',
                     'genre': 'genre:',
                     'duration': 'dauer:',
                     'director': 'regie:',
                     }
        meta_film = copy(self.meta_film)
        for key in meta_film.keys():
            try:
                meta_film[key] = d[translate[key]]
            except KeyError:
                pass
        # do some necessary cleaning
        if meta_film['year']:
            meta_film['year'] = meta_film['year'][-4:]
        if meta_film['duration']:
            meta_film['duration'] = meta_film['duration'].replace('\xa0', ' ')
        # get other data
        img_screenshot = soup.find('img', class_='rev-slidebg')
        if img_screenshot:
            meta_film['img_screenshot'] = img_screenshot.get('src').strip()
        meta_film['img_poster'] = soup.find('img', class_='vc_single_image-img').get('src').strip()
        meta_film['description'] = soup.find('p').text
        return meta_film['title'], meta_film


class City46(Webscraper):

    def create_program_db(self):
        base_url = 'http://www.city46.de/programm/'
        program = []

        urls, years = self.get_urls(base_url)
        for url, year in zip(urls, years):
            html = self.get_html_from_web(url)
            table = self.get_tables_from_html(html)
            if table:
                program.extend(self.extract_program(table, year))
        if not program:
            print(f'!Note, no program could be retrieved from City 46 ({url})')
        return program

    def get_urls(self, url):
        """use today's date to figure out the city 46 program url. If date > 20 also get next month"""
        urls = []
        years = []
        base_link = url
        months = {1: 'januar', 2: 'februar', 3: 'maerz', 4: 'april', 5: 'mai', 6: 'juni', 7: 'juli', 8: 'august',
                  9: 'september', 10: 'oktober', 11: 'november', 12: 'dezember'}

        date = arrow.now('Europe/Berlin')
        year = date.year
        month = date.month
        day = date.day
        full_link = "{}{}-{}.html".format(base_link, months[month], year)
        urls.append(full_link)
        years.append(year)

        if day > 20:
            date = date.shift(months=+1)
            year = date.year
            month = date.month
            full_link = "{}{}-{}.html".format(base_link, months[month], year)
            urls.append(full_link)
            years.append(year)
        return urls, years

    def get_tables_from_html(self, html):
        """Parses all tables from a website. The tables are merged and are saved as a list of
        lists, in which the inner lists are the rows. The cells are stored as bs4.element.Tag.
        Note, it does not handle rowspan or colspan"""
        soup = bs4.BeautifulSoup(html, 'html.parser')

        table = []
        for row in soup.find_all('tr'):  # <tr> = row
            row_list = [cell for cell in row.find_all(['td', 'th'])]  # <td> = data cell <th> = header cell
            table.append(row_list)
        return table

    def clean_rowspan_in_table(self, html_table):
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

    def extract_program(self, html_table, year):
        """ very ugly this, but the HTML is also really ugly.
        save film info in a temporary dictionary that changes throughout the for loop through the table.
        In this for loop the dictionary is saved as a ProgramInfo namedtuple, which is appended to a list. This dictionary
        is exported +/- every time when the loop encounters a time (indicating a new film)"""
        films = []
        temp_dict = {'date': None, 'time': None, 'link': None, 'title': None, 'info': None}
        re_date = re.compile(r"\d{1,2}\.\d{1,2}\.?")  # last .? in case they forget last dot
        re_time = re.compile(r"\d\d:\d\d")

        for row in html_table:
            for cell in row:
                if cell.text:
                    if cell.text in ['MO', 'DI', 'MI', 'DO', 'FR', 'SA', 'SO']:
                        if temp_dict['date'] and temp_dict['title'] and temp_dict['time']:
                            films.append(
                                self.save_programinfo(temp_dict, year))  # 1/3 save the last film of the previous day
                        temp_dict = dict.fromkeys(temp_dict, None)  # remove all values
                    elif re_date.match(cell.text):
                        temp_dict['date'] = self.add_dot_to_date(cell.text)
                    elif re_time.match(cell.text):
                        if temp_dict['date'] and temp_dict['title'] and temp_dict['time']:
                            films.append(self.save_programinfo(temp_dict, year))  # 2/3 save all other films
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
            films.append(self.save_programinfo(temp_dict, year))  # 3/3 save the last movie of the month
        return films

    def add_dot_to_date(self, string):
        """in case they forgot the last dot in the date, add this dot"""
        if string[-1] == '.':
            return string.strip()
        elif string[-1] != '.':
            string = string + '.'
            return string.strip()

    def save_programinfo(self, temp_dict, year):
        title = temp_dict['title']
        datetime = arrow.get(temp_dict['date'] + temp_dict['time'], 'D.M.hh:mm', tzinfo='Europe/Berlin')
        datetime = datetime.replace(year=year)
        link = temp_dict['link']
        info = temp_dict['info']
        programinfo = dict(title=title,
                           datetime=datetime,
                           link_info=link,
                           link_tickets='',
                           location='City46',
                           info=info,
                           price='',
                           artist='',
                           language_version='')
        return programinfo


class TheaterBremen(Webscraper):

    def create_program_db(self):
        program = []
        base_url = 'http://www.theaterbremen.de'
        urls = self.get_urls(base_url)
        for url in urls:
            html = self.get_html_from_web_ajax(url, class_name='day')
            program.extend(self.extract_program(html, base_url))
        if not program:
            print(f'!Note, no program could be retrieved from Theater Bremen ({base_url})')
        return program

    def get_urls(self, base_url):
        """use today's date to figure out the theaterbremen program url. If date > 20 also get next month"""
        urls = []
        base_url = base_url

        date = arrow.now('Europe/Berlin')
        year = date.year
        month = date.month
        day = date.day
        url = "{}#?d={}-{}-{}&f=a".format(base_url, year, month, day)
        urls.append(url)

        if day > 20:
            date = date.shift(months=+1)
            year = date.year
            month = date.month
            url = "{}#?d={}-{}-{}&f=a".format(base_url, year, month, 20)
            urls.append(url)
        return urls

    def extract_program(self, html, base_url):
        # TODO get artist
        program = []
        soup = bs4.BeautifulSoup(html, 'html.parser')
        days = soup.find_all(class_='day')
        if days:
            for day in days:
                date = day.find(class_='date').text.strip()[-10:]
                shows = day.find_all('article')
                for show in shows:
                    time = show.find(class_='overview-date-n-flags').text.strip()[0:5]
                    datetime = arrow.get(date + time, 'DD.MM.YYYYHH:mm', tzinfo='Europe/Berlin')
                    links = show.find_all('a')
                    link_info = '{}{}'.format(base_url, links[0].get('href').strip())
                    try:
                        link_tickets = links[1].get('href').strip()
                        price = links[1].text.strip()
                    except IndexError:
                        link_tickets = ''
                        price = ''
                    title = links[0].text.strip()
                    infos = show.find_all('p')
                    info = '\n'.join(info.text for info in infos)
                    programinfo = dict(title=title,
                                       datetime=datetime,
                                       link_info=link_info,
                                       link_tickets=link_tickets,
                                       location='Theater Bremen',
                                       info=info,
                                       price=price,
                                       artist='',
                                       language_version='')
                    program.append(programinfo)
        else:
            print('Note, no program could be obtained from Theater Bremen')

        return program


class Schwankhalle(Webscraper):

    def create_program_db(self):
        url = 'http://schwankhalle.de/spielplan-1.html'
        # at some point requests starting giving SSLError so use selenium for ajax
        html = self.get_html_from_web_ajax(url, 'date-container')
        program = self.extract_program(html)
        if not program:
            print(f'!Note, no program could be retrieved from Schwankhalle ({url})')
        return program

    def extract_program(self, html):
        program = []
        soup = bs4.BeautifulSoup(html, 'html.parser')

        year = soup.find("td", class_="year-month").text.strip()[0:4]
        table = soup.find('table')
        for row in table.find_all('tr'):  # normal for row in table did not work
            if not isinstance(row, str):  # skip empty table rows
                if row.find(class_='date-container'):
                    date = row.find(class_='date-container').text.strip()
                    date = date + year
                if row.find(class_='time-container'):  # going to assume that a program row always has a time cell
                    time = row.find(class_='time-container').text.strip()[-9:-4]  # in case the time is 'ab ...'
                    if not time:
                        time = '09:00'
                    datetime = arrow.get(date + time, 'D.M.YYYYhh:mm', tzinfo='Europe/Berlin')
                    link = 'https://schwankhalle.de/{}'.format(row.a.get('href').strip())

                    title_artist_info = row.find('td', class_='title')

                    artist = title_artist_info.a.span.text
                    title = title_artist_info.a.text[len(artist) + 1:]  # title is not separated by tags
                    info = title_artist_info.text[len(title) + 1:].strip()  # info is not separated by tags

                    artist = artist.strip()
                    title = title.strip()

                    programinfo = dict(title=title,
                                       artist=artist,
                                       datetime=datetime,
                                       link_info=link,
                                       link_tickets=link,
                                       location='Schwankhalle',
                                       info=info,
                                       price="",
                                       language_version='')
                    program.append(programinfo)
        return program


class Glocke(Webscraper):

    def create_program_db(self):
        base_url = 'https://www.glocke.de/'
        urls = self.get_urls(base_url)
        program = []
        for url in urls:
            html = self.get_html_from_web(url)
            program.extend(self.extract_program(html, base_url))
        if not program:
            print(f'!Note, no program could be retrieved from Glocke ({base_url})')
        return program

    def get_urls(self, base_url):
        arw = arrow.now()
        url1 = base_url + f'/de/Veranstaltungssuche/{arw.month}/{arw.year}'
        arw = arw.shift(months=+1)
        url2 = base_url + f'/de/Veranstaltungssuche/{arw.month}/{arw.year}'
        urls = [url1, url2]
        return urls

    def extract_program(self, html, base_url):
        program = []
        soup = bs4.BeautifulSoup(html, 'html.parser')
        shows = soup.find_all('div', class_='va-liste')
        for show in shows:
            # get time information
            day = int(show.find(class_=re.compile(r"va_liste_datum_1")).text.strip())
            month = show.find(class_=re.compile(r"va_liste_datum_2")).text.strip()
            month = self.german_month_to_int(month)
            time_location = show.find('span', style=re.compile(r"color")).text.strip()
            time = time_location[:6]
            hour = int(time[:2])
            minute = int(time[3:])
            datetime = self.parse_datetime(month, day, hour, minute)

            # get other information
            location_details = time_location[10:]
            title = str(show.find('h2')).strip()
            title = title.replace('<h2>', '')
            title = title.replace('</h2>', '')
            title = title.replace('<br/>', ' - ')
            link = base_url + '{}'.format(show.a.get('href'))

            programinfo = dict(title=title,
                               artist='',
                               datetime=datetime,
                               link_info=link,
                               link_tickets=link,
                               location_details=location_details,
                               location='Glocke',
                               info='',
                               price='',
                               language_version='')
            program.append(programinfo)
        return program


class Kukoon(Webscraper):

    def create_program_db(self):
        url = 'https://kukoon.de/programm/'
        html = self.get_html_from_web(url)
        program = self.extract_program(html)
        return program

    def extract_program(self, html):
        program = []
        soup = bs4.BeautifulSoup(html, 'html.parser')
        shows = soup.find_all('div', class_='event')
        for show in shows:
            datetime = show.time
            if datetime:
                datetime = arrow.get(datetime.get('datetime'))
                title = show.find(class_='event__title').a
                link_info = title.get('href')
                title = title.text.strip()
                location_details = show.find(class_='event__venue').text.strip()
                if location_details == 'Kukoon':
                    location_details = ''
                info = show.find(class_='event__categories').text.strip()

                programinfo = dict(title=title,
                                   artist='',
                                   datetime=datetime,
                                   link_info=link_info,
                                   link_tickets='',
                                   location_details=location_details,
                                   location='Kukoon',
                                   info=info,
                                   price='',
                                   )
                if not 'geschlossene gesellschaft' in title.lower():
                    program.append(programinfo)
        return program
