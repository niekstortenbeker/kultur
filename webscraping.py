import bs4
import requests
import sys
import arrow
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException

# TODO get individual info of the stuff other than ostertor


def start_driver():
    global driver
    firefox_profile = webdriver.FirefoxProfile()
    # disable images
    firefox_profile.set_preference('permissions.default.image', 2)
    # disable flash
    firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
    # Don't disable CSS, filmkunst scraping had issues
    # firefox_profile.set_preference('permissions.default.stylesheet', 2)
    # Disable JavaScript
    firefox_profile.set_preference('javascript.enabled', False)
    driver = webdriver.Firefox(firefox_profile=firefox_profile)


def close_driver():
    driver.quit()

class Webscraper:
    # def __init__(self):
    #     # maybe get some stuff here TODO and how about title/name etc?

    def __repr__(self):
        # TODO maybe actually use this
        return "some information"

    def get_html_from_web(self, url):
        print('...loading webpage')
        try:
            response = requests.get(url)
            if response.status_code == 404:
                print('tried but failed to retrieve html from: ', url)
                return None
            # status = response.status_code
            # print(response.text[0:500])
            else:
                print('Retrieved html from: ', url)
                return response.text
        except requests.exceptions.ConnectionError as e:
            print("Error! Connection error: {}".format(e))
            print('the script is aborted')
            sys.exit(1)

    def get_html_from_web_ajax(self, url, class_name):
        """Get page source code from a web page that uses ajax to load elements of the page one at a time.
         Selenium will wait for the element with the class name 'class_name' to load before getting the page source"""
        print('...loading webpage')
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))
            source = driver.page_source
        except TimeoutException:
            print("Error! Selenium Timeout: {}".format(url))
            print('the script is aborted')
            sys.exit(1)
        except WebDriverException as e:
            print("Error! Selenium Exception. {}".format(str(e)))
            print('the script is aborted')
            sys.exit(1)
        print('Retrieved html from: ', url)
        return source

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


class City46(Webscraper):

    def create_program_db(self):
        base_url = 'http://www.city46.de/programm/'
        program = []

        links = self.get_urls(base_url)
        for link in links:
            html = self.get_html_from_web(link)
            if html:
                table = self.get_tables_from_html(html)
                program.extend(self.extract_program(table))
        return program

    def get_urls(self, url):
        """use today's date to figure out the city 46 program url. If date > 20 also get next month"""
        urls = []
        base_link = url
        months = {1: 'januar', 2: 'februar', 3: 'maerz', 4: 'april', 5: 'mai', 6: 'juni', 7: 'juli', 8: 'august',
                  9: 'september', 10: 'oktober', 11: 'november', 12: 'dezember'}

        date = arrow.now('Europe/Berlin')
        #year = date.year
        month = date.month
        day = date.day
        full_link = "{}{}.html".format(base_link, months[month])  #"{}{}-{}.html".format(base_link, months[month], year)
        urls.append(full_link)

        if day > 20:
            date = date.shift(months=+1)
            year = date.year
            month = date.month
            full_link = "{}{}-{}.html".format(base_link, months[month], year)
            urls.append(full_link)
        return urls

    def extract_program(self, html_table):
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
                        if temp_dict['date'] and temp_dict['title']:
                            films.append(self.save_programinfo(temp_dict))  # 1/3 save the last film of the previous day
                        temp_dict['title'] = None
                    elif re_date.match(cell.text):
                        temp_dict['date'] = self.add_dot_to_date(cell.text)
                    elif re_time.match(cell.text):
                        if temp_dict['date'] and temp_dict['title']:
                            films.append(self.save_programinfo(temp_dict))  # 2/3 save all other films
                        temp_dict['time'] = cell.text.strip()
                    elif cell.find('a'):
                        temp_dict['link'] = 'http://www.city46.de/' + cell.find('a').get('href')
                        title = cell.find('a').text
                        temp_dict['title'] = title
                        temp_dict['info'] = cell.text[len(title):]  # separate the title from the other info
                    else:  # in case there is extra info in the most right column
                        temp_dict['info'] = temp_dict['info'] + ' | ' + cell.text
        films.append(self.save_programinfo(temp_dict))  # 3/3 save the last movie of the month
        return films

    def add_dot_to_date(self, string):
        """in case they forgot the last dot in the date, add this dot"""
        if string[-1] == '.':
            return string.strip()
        elif string[-1] != '.':
            string = string + '.'
            return string.strip()

    def save_programinfo(self, temp_dict):
        if temp_dict['date'] and temp_dict['title']: # skip empty
            title = temp_dict['title']
            datetime = arrow.get(temp_dict['date'] + temp_dict['time'], 'D.M.hh:mm', tzinfo='Europe/Berlin')
            datetime = datetime.replace(year=arrow.now('Europe/Berlin').year)
            link = temp_dict['link']
            info = temp_dict['info']
            programinfo = dict(title=title, datetime=datetime, link_info=link, link_tickets='',
                                    location='City46', info=info, price='', artist='', language_version='')
            return programinfo



class CinemaOstertor(Webscraper):

    def create_program_db(self):
        url = 'http://cinema-ostertor.de/programm/'
        html = self.get_html_from_web(url)
        table = self.get_tables_from_html(html)
        table = self.clean_rowspan_in_table(table)
        program = self.extract_program(table)
        return program

    def extract_program(self, html_table):
        program = []
        day = {}

        for row in html_table:
            for column_number, cell in enumerate(row):
                if cell.name == 'th':
                    date = arrow.get(cell.text, 'DD.MM.YYYY')
                    day[column_number] = date
                elif cell.name == 'td' and cell.text:
                    date = day[column_number]
                    time = cell.find(class_='hours').text
                    datetime = date.replace(hour=int(time[0:2]), minute=int(time[3:5]), tzinfo='Europe/Berlin')
                    title = cell.find('a').text
                    link = cell.find('a').get('href').strip()
                    programinfo = dict(title=title, datetime=datetime, link_info=link, link_tickets='',
                                            location='Cinema Ostertor', info ='', price='', artist='', language_version='')
                    program.append(programinfo)
            # website has a table for the complete program, and tables for individual films. Therefore remove
            # duplicates. Cannot only use first table because sometimes two weeks are displayed.
            program = [dict(t) for t in set([tuple(d.items()) for d in program])]  # remove duplicates
        return program

    def create_meta_db(self, ostertor_programinfo):
        meta_info = {}
        movie_links = set([programinfo['link_info'] for programinfo in ostertor_programinfo])

        for link in movie_links:
            html = self.get_html_from_web(link)
            if html:
                soup = bs4.BeautifulSoup(html, 'html.parser')
                meta_film = {'title': '',
                             'country': '',
                             'year': '',
                             'genre': '',
                             'duration': '',
                             'director': '',
                             'language': '',
                             'description': '',
                             'img_poster': '',
                             'img_screenshot': '',
                             }  # I want keys to be present also if values are absent # TODO oh yeah why?

                title = soup.find(class_='page_title')
                if title:
                    title = title.text.strip()
                    meta_film['title'] = title
                country = soup.find(class_='event_country')
                if country:
                    meta_film['country'] = country.text.strip()
                year = soup.find(class_='event_year')
                if year:
                    meta_film['year'] = year.text.strip()
                genre = soup.find(class_='event_category')
                if genre:
                    meta_film['genre'] = genre.text.strip()
                duration = soup.find(class_='movies_length')
                if duration:
                    meta_film['duration'] = duration.text.strip()
                director = soup.find(class_='event_director')
                if director:
                    meta_film['director'] = director.text.strip()
                language = soup.find(class_='event_language')
                if language:
                    meta_film['language'] = language.text.strip()
                description = soup.find(class_='entry-content')  # description is in two p tags
                if description:
                    description = description.find_all('p')
                    meta_film['description'] = ''.join([p.text for p in description]).strip()
                img_poster = soup.find('img', class_='open_entry_image')
                if img_poster:
                    meta_film['img_poster'] = img_poster.get('src').strip()
                img_screenshot = soup.find('img', class_='alignright')
                if img_screenshot:
                    meta_film['img_screenshot'] = img_screenshot.get('src').strip()

                meta_info[title] = meta_film
        meta_info = {'Cinema Ostertor': meta_info}
        return meta_info


class TheaterBremen(Webscraper):

    def create_program_db(self):
        program = []
        base_url = 'http://www.theaterbremen.de'
        urls = self.get_urls(base_url)
        for url in urls:
            html = self.get_html_from_web_ajax(url, class_name='day')
            program.extend(self.extract_program(html, base_url))
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
            day = date.day
            url = "{}#?d={}-{}-{}&f=a".format(base_url, year, month, day)
            urls.append(url)
        return urls

    def extract_program(self, html, base_url):
        #TODO get artist
        program = []
        soup = bs4.BeautifulSoup(html, 'html.parser')
        days = soup.find_all(class_='day')
        for day in days:
            date = day.find(class_='date').text.strip()[-10:]
            shows = day.find_all('article')
            for show in shows:
                time = show.find(class_='overview-date-n-flags').text.strip()[0:5]
                datetime = arrow.get(date+time, 'DD.MM.YYYYHH:mm', tzinfo='Europe/Berlin')
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
                programinfo = dict(title=title, datetime=datetime, link_info=link_info, link_tickets=link_tickets,
                                        location='Theater Bremen', info=info, price=price, artist='', language_version='')
                program.append(programinfo)
        return program

class Filmkunst(Webscraper):

    def create_program_db(self):
        complete_program = []

        urls_scrape = ['https://www.kinoheld.de/kino-bremen/schauburg-kino-bremen/shows/shows?mode=widget',
                       'https://www.kinoheld.de/kino-bremen/gondel-filmtheater-bremen/shows/shows?mode=widget',
                       'https://www.kinoheld.de/kino-bremen/atlantis-filmtheater-bremen/shows/shows?mode=widget']
        urls_info = ['http://www.bremerfilmkunsttheater.de/Kino_Reservierungen/Schauburg.html',
                     'http://www.bremerfilmkunsttheater.de/Kino_Reservierungen/Gondel.html',
                     'http://www.bremerfilmkunsttheater.de/Kino_Reservierungen/Atlantis.html']
        names = ['Schauburg', 'Gondel', 'Atlantis']

        for idx, url in enumerate(urls_scrape):
            html = self.get_html_from_web_ajax(url, 'movie.u-px-2.u-py-2')
            program = self.extract_program(html, names[idx], urls_info[idx])
            complete_program.extend(program)
        return complete_program

    def extract_program(self, html, location, program_link):
        program = []
        link = 'https://www.kinoheld.de/'
        soup = bs4.BeautifulSoup(html, 'html.parser')
        films = soup.find_all('article')
        for film in films:
            datetime = film.find(class_='movie__date').text
            datetime = Filmkunst.parse_datetime(datetime)
            title = film.find(class_='movie__title').text.strip()
            if title[-3:] in ['OmU', ' OV']:  # do some cleaning to remove white lines from some titles
                title = title[:-3].strip()
            language_version = film.find(class_='movie__flags').text.strip()
            link_tickets = link + film.a.get('href')
            programinfo = dict(title=title, datetime=datetime, link_info=program_link, link_tickets=link_tickets,
                                      location=location, info='', price='', artist='', language_version=language_version)
            program.append(programinfo)
        return program

    def parse_datetime(datetime_string):
        """datetime_string: 'So 08.07. 14:15'. Parse date from this, and guess the year"""
        datetime = arrow.now('Europe/Berlin')
        datetime = datetime.replace(month=int(datetime_string[6:8]), day=int(datetime_string[3:5]),
                                    hour=int(datetime_string[10:12]), minute=int(datetime_string[13:15]),
                                    second=0, microsecond=0)
        if datetime < arrow.now("Europe/Berlin").shift(months=-1):
            return datetime.replace(year=datetime.year + 1)
        else:
            return datetime

    def create_meta_db(self):
        meta_db = {}
        urls = ['https://www.kinoheld.de/kino-bremen/schauburg-kino-bremen/shows/movies?mode=widget',
                'https://www.kinoheld.de/kino-bremen/gondel-filmtheater-bremen/shows/movies?mode=widget',
                'https://www.kinoheld.de/kino-bremen/atlantis-filmtheater-bremen/shows/movies?mode=widget']
        names = ['Schauburg', 'Gondel', 'Atlantis']
        for idx, url in enumerate(urls):
            html = self.get_meta_html(url)
            meta = self.extract_meta(html)
            meta_db[names[idx]] = meta
        return meta_db


    def get_meta_html(self, url):
        """I need to click some buttons to get all the info in the html"""
        print('...loading webpage')
        try:
            driver.get(url)
            # there is an overlay while loading that prevents clicking buttons, even when they are already there
            # it does not click buttons of films without trailers, not sure if this is a problem
            button_class = 'ui-button.ui-corners-bottom-left.ui-ripple.ui-button--secondary.u-flex-grow-1'
            overlay_class = "loading-indicator__background.is-loading"
            WebDriverWait(driver, 10).until_not(EC.visibility_of_element_located((By.CLASS_NAME, overlay_class)))
            buttons = driver.find_elements_by_class_name(button_class)
            for button in buttons:
                button.click()
            source = driver.page_source
        except TimeoutException:
            print("Error! Selenium Timeout: {}".format(url))
            print('the script is aborted')
            sys.exit(1)
        except WebDriverException as e:
            print("Error! Selenium Exception. {}".format(str(e)))
            print('the script is aborted')
            sys.exit(1)
        print('Retrieved html from: ', url)
        return source

    def extract_meta(self, html):
        meta_info = {}
        soup = bs4.BeautifulSoup(html, 'html.parser')
        films = soup.find_all('article')

        for film in films:
            meta_film = {'title': '',
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
                         }  # I want keys to be present also if values are absent

            try:
                dl = film.find(class_='movie__additional-data').find('dl')
                dt = [tag.text.strip().lower() for tag in dl.find_all('dt')]
                dd = [tag.text.strip() for tag in dl.find_all('dd')]
                meta_film['title'] = dd[dt.index('titel')]  # I always need a title
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


class Schwankhalle(Webscraper):

    def create_program_db(self):
        url = 'http://schwankhalle.de/spielplan-1.html'
        # at some point requests starting giving SSLError so use selenium for ajax
        html = self.get_html_from_web_ajax(url,'date-container')
        program = self.extract_program(html)
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
                    title = title_artist_info.a.text[len(artist)+1:]  # title is not separated by tags
                    info = title_artist_info.text[len(title)+1:].strip() # info is not separated by tags

                    artist = artist.strip()
                    title = title.strip()

                    programinfo = dict(title=title, artist=artist, datetime=datetime, link_info=link,
                                              link_tickets=link,
                                              location='Schwankhalle', info=info, price="", language_version='')
                    program.append(programinfo)
        return program


class Glocke(Webscraper):

    def create_program_db(self):
        base_url = 'https://www.glocke.de/de/'
        urls = self.get_urls(base_url)
        program = []
        for url in urls:
            html = self.get_html_from_web(url)
            program.extend(self.extract_program(html, base_url))
        return(program)

    def get_urls(self, base_url):
        month = arrow.now().month
        year = arrow.now().year
        url1 = base_url + f'index.php?showcal=true&kalender_monat=true&month={month}&year={year}&nav=1&sub1=1&sub2=0&seite=66'
        url2 = base_url + f'index.php?showcal=true&kalender_monat=true&month={month+1}&year={year}&nav=1&sub1=1&sub2=0&seite=66'
        urls = [url1, url2]
        return urls

    def extract_program(self, html, base_url):
        program = []
        soup = bs4.BeautifulSoup(html, 'html.parser')

        program_html = soup.find('div', id='inhalt_mitte')
        dates = program_html.find_all('div', class_='va_links')
        other_infos = program_html.find_all('div', class_='va_rechts')
        if not len(dates) == len(other_infos):
            print('oh no dicts are not the same size, check webscraping extract program')
            return None
        for idx, other_info in enumerate(other_infos):
            date = dates[idx].find(class_='va_datum').text.strip()
            month = Glocke.german_month_to_int(self, date[-3:])
            day = date[:2]
            time_location = other_info.find(class_='ort_uhrzeit')
            time = time_location.text.strip()[:6]
            datetime = Glocke.parse_datetime(self, time, day, month)

            location_details = time_location.text.strip()[10:]
            title = other_info.find('br').find_next('br').previous_sibling  # for some reason next_sibling didn't always work
            artist = other_info.find('br').previous_sibling
            link = base_url + '{}'.format(other_info.a.get('href'))
            programinfo = dict(title=title, artist=artist, datetime=datetime, link_info=link,
                               link_tickets=link, location_details=location_details,
                               location='Glocke', info='', price="", language_version='')
            program.append(programinfo)
        return program

    def parse_datetime(self, time, day, month):
        """get arrow object from date from this, and guess the year"""
        datetime = arrow.now('Europe/Berlin')
        datetime = datetime.replace(month=month, day=int(day),
                                    hour=int(time[:2]), minute=int(time[3:]), second=0, microsecond=0)
        if datetime < arrow.now("Europe/Berlin").shift(months=-1):
            return datetime.replace(year=datetime.year + 1)
        else:
            return datetime

