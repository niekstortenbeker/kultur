import webscraping
import arrow
import bs4

def main():
    print_header()
    city46 = create_database_city46()
    ostertor = create_database_cinema_ostertor()
    theater = create_database_theater_bremen()
    # schwankhalle = create_database_schwankhalle()
    # TODO: get Schauburg et al, Schwankhalle
    databases = [city46, ostertor, theater]
    database = merge_databases(databases)
    print_database(database)
    create_database_filmkunst()



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
        html = city46.get_html_from_web(link)  # todo check if this is working on a >20 date.
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
    print('\nWorking on Schauburg')
    url = 'http://www.bremerfilmkunsttheater.de/kino_reservierungen/schauburg.html'
    schauburg = webscraping.Filmkunst()
    html = schauburg.get_html_from_web_ajax_test(url)
    print(html)


def create_database_schwankhalle():
    print('\nWorking on Schwankhalle')
    url = 'http://schwankhalle.de/spielplan-1.html'
    schwankhalle = webscraping.Schwankhalle()
    html = schwankhalle.get_html_from_web(url)
    table = schwankhalle.get_tables_from_html(html)
    table = schwankhalle.clean_rowspan_in_table(table)
    schwankhalle.extract_program(table)


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
    week_later = now.shift(weeks=+1).replace(hour=00, minute=00)
    for programinfo in database:
        if programinfo.datetime > now and programinfo.datetime < week_later:
            if programinfo.datetime.day != day:  # print a day separator
                day = programinfo.datetime.day
                print(''.center(50, '-'))
            print('{} | {} | {} | {} | {} | {}'.format(programinfo.datetime.format('ddd MM-DD HH:mm'),
                                             programinfo.location.center(15, ' '),
                                             programinfo.title,
                                             programinfo.link_info,
                                             programinfo.info.replace('\n', '. '),
                                             programinfo.price))


if __name__ == '__main__':
    main()
