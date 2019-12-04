import file
import helper
import bs4
import arrow
import re
import copy


class CombinedProgram:
    """this is the main functional unit, it is thought to be the only thing to be directly interacted with
    contains blabla"""
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
        city_46 = City46()
        theater_bremen = TheaterBremen()
        schwankhalle = Schwankhalle()
        glocke = Glocke()
        kukoon = Kukoon()
        self.theaters = [
            schauburg,
            gondel,
            atlantis,
            cinema_ostertor,
            city_46,
            theater_bremen,
            schwankhalle,
            glocke,
            kukoon
        ]
        self.program = Program()

    def __repr(self):
        return 'CombinedProgram()'

    def program_from_file(self):
        """use json with
        one file that combines the program.shows
        as a dictionary with theater names as keys and the program.shows
        as values, and one file similarly for meta_info.shows.
        populate these back to the self.theaters, and then refresh self.program
        """
        program, meta, date = file.open_from_file()
        for t in self.theaters:
            if t.name in program:
                t.program = Program(shows=program[t.name])
                t.program.date = date
        for t in self.theaters:
            if t.name in meta:
                t.meta_info = MetaInfo(shows=meta[t.name])
                t.meta_info.date = date
        self._refresh_program(date=date)

    def _program_to_file(self):
        """for all self.theaters, make one file that combines the program.shows
        as a dictionary with theater names as keys and the program.shows
        as values, and one file similarly for meta_info.shows """
        program_db = {t.name: t.program.shows for t in self.theaters}
        program_db = copy.deepcopy(program_db)
        meta_db = {t.name: t.meta_info.shows for t in self.theaters}
        meta_db = copy.deepcopy(meta_db)
        file.save_to_file(program_db, meta_db)

    def update_program(self):
        """
        update the complete program

        The program is updated both in the theater.program of self.theaters,
        and in self.program.
        """
        # update program
        helper.start_driver()
        for t in self.theaters:
            t.update_program()
        # update meta info
        meta_theaters = ['Schauburg', 'Gondel', 'Atlantis', 'Cinema Ostertor']
        for t in self.theaters:
            if t.name in meta_theaters:
                t.update_meta_info()
                t.annotate_dubbed_films()
        helper.close_driver()
        self._refresh_program(date=arrow.now())
        self._program_to_file()

    def _refresh_program(self, date):
        """make a new self.program based on the programs in self.theaters"""
        self.program.empty()
        for t in self.theaters:
            try:
                self.program = self.program + t.program
            except AttributeError:  # if theater has None as program
                continue
        self.program.sort()
        self.program.date = date


class Program:
    """should be initialized with either shows: a list of Show objects, or
    a list of ShowMetaInfo objects, or with None

    show dict should have
    self.date_time = date_time
    show dict could have
        self.title = ''
        self.artist = ''
        self.link_info = ''
        self.link_tickets = ''
        self.location_details = ''
        self.location = ''
        self.info = ''
        self.price = ''
        self.language_version = ''

    """

    def __init__(self, shows=None):
        """shows should be a list of Show or ShowMetaInfo objects or absent"""
        self.shows = shows if shows else []
        self.date = arrow.get(0)

    def __repr__(self):
        return f'Program({self.shows})'

    def __str__(self):
        return self.shows

    def __add__(self, other):
        shows = self.shows + other.shows
        return Program(shows)

    def __len__(self):
        return len(self.shows)

    def __iter__(self):
        return iter(self.shows)

    def __contains__(self, item):
        return item in [s['title'] for s in self.shows]

    def empty(self):
        self.shows = []

    def sort(self):
        self.shows.sort(key=lambda show: show['date_time'])

    def print_next_week(self):
        """get the program of the next week. If today=True instead get only today
        """
        now = arrow.utcnow()
        stop_day = now.shift(weeks=+1).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo='Europe/Berlin')
        self.print(program=self._filter_program(stop_day))

    def print_today(self):
        now = arrow.utcnow()
        stop_day = now.shift(days=+1).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo='Europe/Berlin')
        self.print(program=self._filter_program(stop_day))

    def _filter_program(self, stop_day):
        program = []
        now = arrow.utcnow()
        for show in self.shows:
            if show['date_time'] < now:
                continue
            elif show['date_time'] > stop_day:
                break
            elif show.get('is_probably_dubbed_film'):
                continue
            else:
                program.append(show)
        return program

    def print(self, program=None):
        if not program:
            program = self.shows
        print(f'\nthis program uses a database made {self.date.humanize()}')
        print(''.center(50, '-'))
        old_day = program[0]['date_time'].date()
        for s in program:
            # print day separator
            day = s['date_time'].date()
            if day != old_day:
                print(''.center(50, '-'))
                old_day = day
            # print program
            print('{} | {} | {} {} | {} | {} | {}'.format(
                s['date_time'].format('ddd MM-DD HH:mm'),
                s.get('location', ''),
                s.get('artist', ''),
                s.get('title', ''),
                s.get('link_info', ''),
                s.get('info', ''),
                s.get('price', '')
            ))


class MetaInfo:
    """should be initialized with
    a list of ShowMetaInfo objects, or with None


    show metainfo dict should have
    self.title = title
    show metainfo dict could have
        self.title_original = ''
        self.country = ''
        self.year = ''
        self.genre = ''
        self.duration = ''
        self.director = ''
        self.language = ''
        self.description = ''
        self.img_poster = ''
        self.img_screenshot = ''
        self.link_info = ''


    """

    def __init__(self, shows=None):
        """shows should be a list of Show or ShowMetaInfo objects or absent"""
        self.shows = shows if shows else []
        self.date = arrow.get(0)

    def __repr__(self):
        return f'MetaInfo({self.shows})'

    def __str__(self):
        return self.shows

    def __add__(self, other):
        shows = self.shows + other.shows
        return Program(shows)

    def __len__(self):
        return len(self.shows)

    def __iter__(self):
        return iter(self.shows)

    def __contains__(self, item):
        return item in self.shows

    def sort(self):
        self.shows.sort(key=lambda show: show['title'])

    def get(self, title):
        return self.shows[title]


class Theater:
    """Theater class should not be instantiated directly, but only be used
    to inherit from"""

    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.program = Program()
        self.meta_info = MetaInfo()

    def __repr__(self):
        return f'Theater({self.name, self.url})'

    def __str__(self):
        return f'Theater({self.name})'

    def update_program(self):
        """uses _get_shows() which should be an available method in each child
        class. maybe explain here or in the dummmy method which keys should and
        could be present"""
        print(f'\n updating program {self.name}')
        try:
            shows = self._get_shows()
            self.program = Program(shows)
            self.program.sort()
        except (TypeError, AttributeError, ValueError) as e:
            print(f"Note! Program from {self.name} was not updated because of an error: {e}")

    def _get_shows(self):
        """a dummy method that should be overridden by child classes"""
        print('Note! _get_shows() should be present in the child class')
        return True

    def annotate_dubbed_films(self):
        for s in self.program.shows:
            if self._film_is_probably_dubbed(s):
                s['is_probably_dubbed_film'] = True

    def _film_is_probably_dubbed(self, show):
        if show['language_version']:  # OMUs and OV
            return False
        elif self._is_german(show['title']):  # should be in child
            return False
        else:
            return True

    def _is_german(self, title):
        """a dummy method that should be overridden by child classes"""
        print('Note! _is_german() should be present in the child class')
        return False


class Kinoheld(Theater):

    def __init__(self, name, url_program_info, url_program_scrape, url_meta):
        super().__init__(name, url_program_info)
        self.url_program_scrape = url_program_scrape
        self.url_meta = url_meta

    def _get_shows(self):
        html = helper.get_html_ajax(self.url_program_scrape, 'movie.u-px-2.u-py-2')
        return self._extract_show_list(html)

    def _extract_show_list(self, html):
        show_list = []
        soup = bs4.BeautifulSoup(html, 'html.parser')
        shows = soup.find_all('article')
        for s in shows:
            date_time = s.find(class_='movie__date').text
            month, day = int(date_time[6:8]), int(date_time[3:5])
            hour, minute = int(date_time[10:12]), int(date_time[13:15])
            date_time = helper.parse_date_without_year(month, day, hour, minute)
            show = {'date_time': date_time}
            title = s.find(class_='movie__title').text.strip()
            if title[-3:] in ['OmU', ' OV', 'mdU', 'meU']:
                title = title[:-3].strip()
            show['title'] = title
            if s.find(class_='movie__title').span:
                show['language_version'] = s.find(class_='movie__title').span.text.strip()
            else:
                show['language_version'] = ''
            show['link_tickets'] = 'https://www.kinoheld.de/' + s.a.get('href')
            show['link_info'] = self.url
            show['location'] = self.name
            show_list.append(show)
        return show_list

    def update_meta_info(self):
        print(f'\n updating meta info {self.name}')
        button_classes = ['ui-button.ui-corners-bottom-left.ui-ripple.ui-button--secondary.u-flex-grow-1',
                          'ui-button.ui-corners-bottom.ui-ripple.ui-button--secondary.u-flex-grow-1']
        overlay_class = "overlay-container"
        html = helper.get_html_buttons(self.url_meta, button_classes, overlay_class)
        try:
            meta = self._extract_meta(html)
            self.meta_info = MetaInfo(meta)
        except (TypeError, AttributeError, ValueError):
            print(f"Note! Meta info from {self.name} was not updated because of an error")

    def _extract_meta(self, html):
        meta_info = {}
        soup = bs4.BeautifulSoup(html, 'html.parser')
        films = soup.find_all('article')
        # TODO: organize this more like in cinema ostertor. I think I'm missing a lot
        for film in films:
            try:
                dl = film.find(class_='movie__additional-data').find('dl')
                dt = [tag.text.strip().lower() for tag in dl.find_all('dt')]
                dd = [tag.text.strip() for tag in dl.find_all('dd')]
                meta_film = {}
                meta_film['title'] = dd[dt.index('titel')]
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
                meta_film['description'] = film.find('div', class_='movie__info-description').text
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

    def _is_german(self, title):
        """
        Test if film is made in a german speaking country

        :param title: string
        :param location_name: string with Theater name (e.g. Ostertor)
        :param db_metainfo: list of ShowMetaInfo objects
        :return: True if from German speaking country
        """

        try:
            # this info is hidden in the first part of the description
            country = self.meta_info.get(title)['description'][0:100].lower()
            # Otherwise if it is made in a german speaking country chances are it's not dubbed
            if 'deutschland' in country:
                return True
            elif 'österreich' in country:
                return True
            elif 'schweiz' in country:
                return True
            else:
                return False
        except KeyError:
            return False


class CinemaOstertor(Kinoheld):
    # TODO use url from meta info for program_link

    def __init__(self):
        url = 'https://cinema-ostertor.de/programm'
        super().__init__(name='Cinema Ostertor',
                         url_program_info=url,
                         url_program_scrape='https://www.kinoheld.de/kino-bremen/cinema-im-ostertor-bremen/shows/shows?mode=widget',
                         url_meta=url)

    def update_meta_info(self):
        print(f'\n updating meta info {self.name}')
        try:
            urls = self._get_meta_urls()
            meta = self._extract_meta(urls)
            self.meta_info = MetaInfo(meta)
        except (TypeError, AttributeError, ValueError):
            print(f"Note! meta info from {self.name} was not updated because of an error")

    def _get_meta_urls(self):
        html = helper.get_html(self.url_meta)
        soup = bs4.BeautifulSoup(html, 'html.parser')
        urls = [url.get('href').strip() for url in soup.find_all('a', class_='elementor-post__read-more')]
        return set(urls)

    def _extract_meta(self, movie_urls):
        meta_info_program = {}
        for url in movie_urls:
            html = helper.get_html(url)
            try:
                meta_info_show = self._parse_show(html)
                meta_info_program[meta_info_show['title']] = meta_info_show
            except TypeError:
                print(f"No meta info was extracted because of a NoneType (url: {url})")
        return meta_info_program

    # noinspection PyMethodMayBeStatic
    def _parse_show(self, html):
        """from a html page with supposedly film info extract meta info in a ShowMetaInfo object.
        Return the title and the object. Should return a None if it doesn't work"""
        soup = bs4.BeautifulSoup(html, 'html.parser')
        # many stats are hidden in a sloppy bit of html
        # in case there is a web page that doesn't display a normal film have this bit in a try except block
        try:
            stats = soup.find('div', class_='elementor-element-bf542d7')
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
            meta_film = {'title': d['titel:']}
        except KeyError:  # If I can't parse the title I don't want anything
            return None
        for key in translate.keys():
            try:
                meta_film[key] = d[translate[key]]
            except KeyError:
                continue
        # do some necessary cleaning
        if 'year' in meta_film:
            meta_film['year'] = meta_film['year'][-4:]
        if 'duration' in meta_film:
            meta_film['duration'] = meta_film['duration'].replace('\xa0', ' ')
        poster = soup.find('div', class_='elementor-element-f5652a8')
        meta_film['img_poster'] = poster.find('img').get('src').strip()
        meta_film['description'] = soup.find('p').text
        return meta_film

    def _is_german(self, title):
        """
        Test if film is made in a german speaking country

        :param title: string
        :param location_name: string with Theater name (e.g. Ostertor)
        :param db_metainfo: list of ShowMetaInfo objects
        :return: True if from German speaking country
        """
        try:
            # TODO also check for title and original title if this is passed
            country = self.meta_info.get(title)['country'].lower()
            # Otherwise if it is made in a german speaking country chances are it's not dubbed
            if 'deutschland' in country:
                return True
            elif 'österreich' in country:
                return True
            elif 'schweiz' in country:
                return True
            else:
                return False
        except KeyError:
            return False


class City46(Theater):

    def __init__(self):
        super().__init__('City 46', 'http://www.city46.de/programm/')

    def _get_shows(self):
        # TODO maybe use pandas pd.read_html(str(soup.find('table')))[0]
        shows = []
        urls, years = self._get_urls()
        for url, year in zip(urls, years):
            html = helper.get_html(url)
            table = self._get_tables_from_html(html)
            shows.extend(self._extract_show_list(table))
        return shows

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

    def _extract_show_list(self, html_table):
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
                                self._save_show(temp_dict))  # 1/3 save the last film of the previous day
                        temp_dict = dict.fromkeys(temp_dict, None)  # remove all values
                    elif re_date.match(cell.text):
                        temp_dict['date'] = self._add_dot_to_date(cell.text)
                    elif re_time.match(cell.text):
                        if temp_dict['date'] and temp_dict['title'] and temp_dict['time']:
                            show_list.append(self._save_show(temp_dict))  # 2/3 save all other films
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
            show_list.append(self._save_show(temp_dict))  # 3/3 save the last movie of the month
        return show_list

    def _add_dot_to_date(self, string):
        """in case they forgot the last dot in the date, add this dot"""
        if string[-1] == '.':
            return string.strip()
        elif string[-1] != '.':
            string = string + '.'
            return string.strip()

    def _save_show(self, temp_dict):
        show = {}
        date_time = arrow.get(temp_dict['date'] + temp_dict['time'], 'D.M.hh:mm', tzinfo='Europe/Berlin')
        show['date_time'] = helper.parse_date_without_year(date_time)
        show['title'] = temp_dict['title']
        show['link_info'] = temp_dict['link']
        show['info'] = temp_dict['info']
        show['location'] = self.name
        return show


class TheaterBremen(Theater):
    def __init__(self):
        super().__init__('Theater Bremen', 'http://www.theaterbremen.de')

    def _get_shows(self):
        shows = []
        urls = self._get_urls()
        for url in urls:
            html = helper.get_html_ajax(url, class_name='day')
            shows.extend(self._extract_show_list(html))
        return shows

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
                show = {}
                time = s.find(class_='overview-date-n-flags').text.strip()[0:5]
                show['date_time'] = arrow.get(date + time, 'DD.MM.YYYYHH:mm', tzinfo='Europe/Berlin')
                links = s.find_all('a')
                show['link_info'] = '{}{}'.format(self.url, links[1].get('href').strip())
                try:
                    show['link_tickets'] = links[2].get('href').strip()
                    show['price'] = links[2].text.strip()
                except IndexError:
                    pass
                show['title'] = links[1].text.strip()
                infos = s.find_all('p')
                show['info'] = '\n'.join(info.text for info in infos)  #TODO remove white lines
                show['location'] = self.name
                show_list.append(show)
        return show_list


class Schwankhalle(Theater):

    def __init__(self):
        super().__init__('Schwankhalle', 'http://schwankhalle.de/spielplan-1.html')

    def _get_shows(self):
        # TODO fix scraping problem
        # at some point requests starting giving SSLError so use selenium for ajax
        html = helper.get_html_ajax(self.url, 'date-container')
        return self._extract_show_list(html)

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
            show = {}
            show['date_time'] = self._get_date_time(row, year)
            title_artist_info = row.find('td', class_='title')
            artist = title_artist_info.a.span.text
            title = title_artist_info.a.text[len(artist) + 1:]  # title is not separated by tags
            show['info'] = title_artist_info.text[len(title) + 1:].strip()  # info is not separated by tags
            show['artist'] = artist.strip()
            show['title'] = title.strip()
            link = 'https://schwankhalle.de/{}'.format(row.a.get('href').strip())
            show['link_info'] = link
            show['link_tickets'] = link
            show['location'] = self.name
            show_list.append(show)
        return show_list

    # noinspection PyMethodMayBeStatic
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

    def _get_shows(self):
        urls = self._get_urls()
        shows = []
        for url in urls:
            html = helper.get_html(url)
            shows.extend(self._extract_show_list(html))
        return shows

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
            show = {}
            date_time, location_details = self._get_date_time_and_location_details(s)
            show['date_time'] = date_time
            show['location_details'] = location_details
            # TODO can this be in less lines
            title = str(s.find('h2')).strip()
            title = title.replace('<h2>', '')
            title = title.replace('</h2>', '')
            title = title.replace('<br/>', ' - ')
            show['title'] = title
            link = self.url + '{}'.format(s.a.get('href'))
            show['link_info'] = link
            show['link_tickets'] = link
            show['location'] = self.name
            show_list.append(show)
        return show_list

    # noinspection PyMethodMayBeStatic
    def _get_date_time_and_location_details(self, show):
        day = int(show.find(class_=re.compile(r"va_liste_datum_1")).text.strip())
        month = show.find(class_=re.compile(r"va_liste_datum_2")).text.strip().lower()
        months = {'jan': 1, 'feb': 2, 'mär': 3, 'maer': 3, 'märz': 3, 'apr': 4, 'mai': 5, 'jun': 6, 'jul': 7,
                  'aug': 8, 'sep': 9, 'sept': 9, 'okt': 10, 'nov': 11, 'dez': 12}
        month = months[month]
        time_location = show.find('span', style=re.compile(r"color")).text.strip()
        hour, minute = int(time_location[:2]), int(time_location[3:6])
        date_time = helper.parse_date_without_year(month, day, hour, minute)
        location_details = time_location[10:]
        return date_time, location_details


class Kukoon(Theater):

    def __init__(self):
        super().__init__('Kukoon', 'https://kukoon.de/programm/')

    def _get_shows(self):
        html = helper.get_html(self.url)
        return self._extract_show_list(html)

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
            show = {'date_time': arrow.get(date_time.get('datetime'))}
            show['link_info'] = title_link.get('href')
            show['title'] = title_link.text.strip()
            location_details = s.find(class_='event__venue').text.strip()
            if not location_details == self.name:
                show['location_details'] = location_details
            show['info'] = s.find(class_='event__categories').text.strip()
            show['location'] = self.name
            show_list.append(show)
        return show_list
