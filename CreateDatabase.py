import webscraping


# TODO save to some database, or maybe start easy with JSON


def main():
    city46_program = create_db_city46()
    theater_program = create_db_theater_bremen()
    filmkunst_program = create_db_filmkunst()
    schwankhalle_program = create_db_schwankhalle()
    ostertor_program, ostertor_meta = create_db_cinema_ostertor()

    program_db = [city46_program, theater_program, filmkunst_program, schwankhalle_program, ostertor_program]
    program_db = merge_databases(program_db)

    # glocke = create_database_glocke()
    return program_db, ostertor_meta

def print_header():
    print(''.center(50, '-'))
    print('KULTUR FACTORY'.center(50, ' '))
    print(''.center(50, '-'))


def create_db_city46():
    print('\nWorking on City 46')
    city46 = webscraping.City46()
    program = city46.create_program_db()
    print('Done with City 46!')
    return program


def create_db_cinema_ostertor():
    print('\nWorking on Cinema Ostertor')
    ostertor = webscraping.CinemaOstertor()
    program = ostertor.create_program_db()
    meta = ostertor.create_meta_db(program)
    print('Done with Cinema Ostertor!')
    return program, meta


def create_db_theater_bremen():
    print('\nWorking on Theater Bremen')
    theater_bremen = webscraping.TheaterBremen()
    program = theater_bremen.create_program_db()
    print('Done with Theater Bremen!')
    return program


def create_db_filmkunst():
    print('\nWorking on Bremer Filmkunst Theater')
    filmkunst = webscraping.Filmkunst()
    program = filmkunst.create_program_db()
    print('Done with filmkunst!')
    return program


def create_db_schwankhalle():
    print('\nWorking on Schwankhalle')
    schwankhalle = webscraping.Schwankhalle()
    program = schwankhalle.create_program_db()
    print('Done with Schwankhalle!')
    return program


def create_database_glocke():
    """ only does the first five things because I'm lazy"""
    print('Working on Glocke')
    url = 'https://www.glocke.de/de/Home'
    glocke = webscraping.Glocke()
    html = glocke.get_html_from_web(url)
    #TODO finish glocke
    print(html)


def merge_databases(databases):
    database = []
    for x in databases:
        database.extend(x)
    database.sort(key=lambda programinfo: programinfo.datetime)
    return database


if __name__ == '__main__':
    main()
