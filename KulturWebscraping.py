import webscraping
import arrow


# TODO maybe use this in some way https://www.omdbapi.com/ or maybe this because this works for german titles too https://www.themoviedb.org/documentation/api?language=de-DE
# TODO filter all non OMUs out, unless they are german original language
# TODO save to some database, or maybe start easy with JSON
# TODO make this automatic
# todo get individual info of the stuff

def main():
    print_header()

    city46 = create_database_city46()
    # ostertor = create_database_cinema_ostertor()
    theater = create_database_theater_bremen()
    filmkunst = create_database_filmkunst()
    schwankhalle = create_database_schwankhalle()

    databases = [city46, theater, filmkunst, schwankhalle]
    database = merge_databases(databases)
    print_database(database)




def print_header():
    print(''.center(50, '-'))
    print('KULTUR FACTORY'.center(50, ' '))
    print(''.center(50, '-'))


def create_database_city46():
    print('\nWorking on City 46')
    program = []
    base_url = 'http://www.city46.de/programm/'
    city46 = webscraping.City46()
    links = city46.get_urls(base_url)
    for link in links:
        html = city46.get_html_from_web(link)
        # html = open('city46.html', 'r')
        table = city46.get_tables_from_html(html)
        program.extend(city46.extract_program(table))
    program = city46.cleanup_programinfo(program)
    print('Done with City 46!')
    return program


def create_database_cinema_ostertor():
    print('\nWorking on Cinema Ostertor')
    url = 'http://cinema-ostertor.de/programm/'
    ostertor = webscraping.CinemaOstertor()
    html = ostertor.get_html_from_web(url)
    # html = open('ostertor.html', 'r')
    table = ostertor.get_tables_from_html(html)
    table = ostertor.clean_rowspan_in_table(table)
    program = ostertor.extract_program(table)
    program = ostertor.cleanup_programinfo(program)
    print('Done with Cinema Ostertor!')
    return program


def create_database_theater_bremen():
    program = []
    print('\nWorking on Theater Bremen')
    base_url = 'http://www.theaterbremen.de'
    theater_bremen = webscraping.TheaterBremen()
    urls = theater_bremen.get_urls(base_url)
    for url in urls:
        html = theater_bremen.get_html_from_web_ajax(url, class_name='day')
        # html = open('theater.html', 'r')
        program.extend(theater_bremen.extract_program(html, base_url))
    print('Done with Theater Bremen!')
    return program


def create_database_filmkunst():
    complete_program = []
    print('\nWorking on Bremer Filmkunst Theater')

    urls_scrape = ['https://www.kinoheld.de/kino-bremen/schauburg-kino-bremen/shows/shows?mode=widget',
                   'https://www.kinoheld.de/kino-bremen/gondel-filmtheater-bremen/shows/shows?mode=widget',
                   'https://www.kinoheld.de/kino-bremen/atlantis-filmtheater-bremen/shows/shows?mode=widget']
    urls_info = ['http://www.bremerfilmkunsttheater.de/Kino_Reservierungen/Schauburg.html',
                 'http://www.bremerfilmkunsttheater.de/Kino_Reservierungen/Gondel.html',
                 'http://www.bremerfilmkunsttheater.de/Kino_Reservierungen/Atlantis.html']
    names = ['Schauburg', 'Gondel', 'Atlantis']

    for idx, url in enumerate(urls_scrape):
        filmkunst = webscraping.Filmkunst()
        html = filmkunst.get_html_from_web_ajax(url, 'movie.u-px-2.u-py-2')
        program = filmkunst.extract_program(html, names[idx], urls_info[idx])
        complete_program.extend(program)

    print('Done with filmkunst!')
    return complete_program


def create_database_schwankhalle():
    print('\nWorking on Schwankhalle')
    url = 'http://schwankhalle.de/spielplan-1.html'
    schwankhalle = webscraping.Schwankhalle()
    html = schwankhalle.get_html_from_web_ajax(url, 'date-container') # at some point requests starting giving SSLError
    program = schwankhalle.extract_program(html)
    print('Done with Schwankhalle!')
    return program


def merge_databases(databases):
    database = []
    for x in databases:
        database.extend(x)
    database.sort(key=lambda programinfo: programinfo.datetime)
    return database


def print_database(database):
    print()
    print(''.center(50, '-'))
    print('PROGRAM'.center(50, ' '))
    print(''.center(50, '-'))
    print()
    day = arrow.utcnow().day  # necessary to print lines between days
    now = arrow.utcnow()
    week_later = now.shift(weeks=+1).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo='Europe/Berlin')
    for programinfo in database:
        if programinfo.datetime > now and programinfo.datetime < week_later:
            if programinfo.datetime.day != day:  # print a day separator
                day = programinfo.datetime.day
                print(''.center(50, '-'))
            if programinfo.location in ['Schauburg', 'Gondel', 'Atlantis']:
                if programinfo.language_version:
                    print_programinfo(programinfo) # only print OMUs and OV, skipping german stuff now
                    # TODO print stuf that is in german original
                    # TODO only print cinema ostertor in original (now skipping everything)
            else:
                print_programinfo(programinfo)


def print_programinfo(programinfo):
    print('{} | {} | {} {} | {} | {} | {}'.format(programinfo.datetime.format('ddd MM-DD HH:mm'),
                                                 programinfo.location.center(15, ' '),
                                                 programinfo.artist,
                                                 programinfo.title,
                                                 programinfo.link_info,
                                                 programinfo.info.replace('\n', '. '),
                                                 programinfo.price))

if __name__ == '__main__':
    main()
