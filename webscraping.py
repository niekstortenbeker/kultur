import bs4
import requests
import sys
import arrow
import collections
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException

ProgramInfo = collections.namedtuple('ProgramInfo',
                                     'title, datetime, link_info, link_tickets, location, info, price')


class Webscraper:
    # def __init__(self):
    #     # maybe get some stuff here TODO and how about title/name etc?

    def __repr__(self):
        # TODO maybe actually use this
        return "some information"

    def get_html_from_web(self, url):
        try:
            response = requests.get(url)
            # status = response.status_code
            # print(response.text[0:500])
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
            driver = webdriver.Firefox()
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
        finally:
            driver.close()
        print('Retrieved html from: ', url)
        return source

    def get_html_from_web_ajax_test(self, url): #TODO make this shit work
        """Get page source code from a web page that uses ajax to load elements of the page one at a time.
         Selenium will wait for the element with the class name 'class_name' to load before getting the page source"""
        print('...loading webpage')
        try:
            driver = webdriver.Firefox()
            driver.get(url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(()))
            source = driver.page_source
        except TimeoutException:
            print("Error! Selenium Timeout: {}".format(url))
            print('the script is aborted')
            sys.exit(1)
        except WebDriverException as e:
            print("Error! Selenium Exception. {}".format(str(e)))
            print('the script is aborted')
            sys.exit(1)
        finally:
            driver.close()
        print('Retrieved html from: ', url)
        return source

    def get_tables_from_html(self, html):
        """Parses all tables from a website. The tables are merged and are saved as a list of
        lists, in which the inner lists are the rows. The cells are stored as bs4.element.Tag.
        Note, it does not handle rowspan or colspan"""
        soup = bs4.BeautifulSoup(html, 'html.parser')
        html_tables = soup.find_all('table')

        table = []
        for html_table in html_tables:
            for row in html_table.find_all('tr'):  # <tr> = row
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

    def cleanup_programinfo(self, programinfo):
        """ remove None's, remove duplicates"""
        programinfo = [show for show in programinfo if show is not None]
        programinfo = list(set(programinfo))  # remove duplicates
        return programinfo


class City46(Webscraper):

    def get_urls(self, url):
        """use today's date to figure out the city 46 program url. If date > 20 also get next month"""
        urls = []
        base_link = url
        months = {1: 'januar', 2: 'februar', 3: 'maerz', 4: 'april', 5: 'mai', 6: 'juni', 7: 'juli', 8: 'august',
                  9: 'september', 10: 'oktober', 11: 'november', 12: 'dezember'}

        date = arrow.now('Europe/Berlin')
        year = date.year
        month = date.month
        day = date.day
        full_link = "{}{}-{}.html".format(base_link, months[month], year)
        urls.append(full_link)

        if day > 20:
            date = date.shift(months=+1)
            year = date.year
            month = date.month
            full_link = "{}{}-{}.html".format(base_link, months[month], year)
            urls.append(full_link)
        return urls

    def extract_program(self, html_table):
        """ save film info in a temporary dictionary that changes throughout the for loop through the table.
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
                        films.append(self.save_programinfo(temp_dict))  # 1/3 save the last film of the previous day
                        temp_dict['title'] = None
                    elif re_date.match(cell.text):
                        temp_dict['date'] = self.add_dot_to_date(cell.text)
                    elif re_time.match(cell.text):
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

    def save_programinfo(self, dict):
        if dict['date'] is not None and dict['title'] is not None:
            title = dict['title']
            datetime = arrow.get(dict['date'] + dict['time'], 'D.M.hh:mm', tzinfo='Europe/Berlin')
            datetime = datetime.replace(year=arrow.now('Europe/Berlin').year)
            link = dict['link']
            info = dict['info']
            programinfo = ProgramInfo(title=title, datetime=datetime, link_info=link, link_tickets=None,
                                    location='City46', info=info, price='') #TODO kloppen die links?
            return programinfo
        else:
            return None


class CinemaOstertor(Webscraper):

    def extract_program(self, html_table):
        films = []
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
                    link = cell.find('a').get('href')

                    programinfo = ProgramInfo(title=title, datetime=datetime, link_info=link, link_tickets=None,
                                            location='Cinema Ostertor', info ='', price='')
                    films.append(programinfo)
        return films


class TheaterBremen(Webscraper):

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
                programinfo = ProgramInfo(title=title, datetime=datetime, link_info=link_info, link_tickets=link_tickets,
                                        location='Theater Bremen', info=info, price=price)
                program.append(programinfo)
        return program

class Filmkunst(Webscraper):

    def extract_program(self, html):
        pass


class Schwankhalle(Webscraper):

    def extract_program(self, table):
        """ save film info in a temporary dictionary that changes throughout the for loop through the table.
                In this for loop the dictionary is saved as a ProgramInfo namedtuple, which is appended to a list. This dictionary
                is exported +/- every time when the loop encounters a time (indicating a new film)"""
        program = []
        temp_dict = {'date': None, 'time': None, 'link': None, 'title': None, 'info': None}
        re_date = re.compile(r"\d{1,2}\.\d{1,2}\.?")  # last .? in case they forget last dot
        re_time = re.compile(r"\d\d:\d\d")

        for row in table:
            for cell in row:
                pass
        #                 program.append(self.save_programinfo(temp_dict))  # 1/3 save the last film of the previous day
        #                 temp_dict['title'] = None
        #             elif re_date.match(cell.text):
        #                 temp_dict['date'] = self.add_dot_to_date(cell.text)
        #             elif re_time.match(cell.text):
        #                 program.append(self.save_programinfo(temp_dict))  # 2/3 save all other films
        #                 temp_dict['time'] = cell.text.strip()
        #             elif cell.find('a'):
        #                 temp_dict['link'] = 'http://www.city46.de/' + cell.find('a').get('href')
        #                 title = cell.find('a').text
        #                 temp_dict['title'] = title
        #                 temp_dict['info'] = cell.text[len(title):]  # separate the title from the other info
        #             else:  # in case there is extra info in the most right column
        #                 temp_dict['info'] = temp_dict['info'] + ' | ' + cell.text
        # program.append(self.save_programinfo(temp_dict))  # 3/3 save the last movie of the month
        # return program

    def save_programinfo(self, dict):
        if dict['date'] is not None and dict['title'] is not None:
            title = dict['title']
            datetime = arrow.get(dict['date'] + dict['time'], 'D.M.hh:mm', tzinfo='Europe/Berlin')
            datetime = datetime.replace(year=arrow.now('Europe/Berlin').year)
            link = dict['link']
            info = dict['info']
            programinfo = ProgramInfo(title=title, datetime=datetime, link_info=link, link_tickets=None,
                                    location='City46', info=info, price='') #TODO kloppen die links?
            return programinfo
        else:
            return None

    def add_dot_to_date(self, string):
        """in case they forgot the last dot in the date, add this dot"""
        if string[-1] == '.':
            return string.strip()
        elif string[-1] != '.':
            string = string + '.'
            return string.strip()