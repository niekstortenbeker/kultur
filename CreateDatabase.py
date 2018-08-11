import webscraping


def main():
    print('\nScraping the program web pages')
    webscraping.start_driver()
    city46_program = create_db_city46()
    theater_program = create_db_theater_bremen()
    filmkunst_program, filmkunst_meta = create_db_filmkunst()
    schwankhalle_program = create_db_schwankhalle()
    ostertor_program, ostertor_meta = create_db_cinema_ostertor()
    glocke_program = create_database_glocke()
    webscraping.close_driver()

    program_db = [city46_program, theater_program, filmkunst_program, schwankhalle_program, ostertor_program,
                  glocke_program]
    program_db = merge_databases(program_db)

    meta_db = {**ostertor_meta, **filmkunst_meta}

    return program_db, meta_db


def print_header():
    print(''.center(50, '-'))
    print('KULTUR FACTORY'.center(50, ' '))
    print(''.center(50, '-'))


def create_db_city46():
    print('\n  Working on City 46')
    city46 = webscraping.City46()
    program = city46.create_program_db()
    return program


def create_db_cinema_ostertor():
    print('\n  Working on Cinema Ostertor')
    ostertor = webscraping.CinemaOstertor()
    program = ostertor.create_program_db()
    meta = ostertor.create_meta_db(program)
    return program, meta


def create_db_theater_bremen():
    print('\n  Working on Theater Bremen')
    theater_bremen = webscraping.TheaterBremen()
    program = theater_bremen.create_program_db()
    return program


def create_db_filmkunst():
    print('\n  Working on Bremer Filmkunst Theater')
    filmkunst = webscraping.Filmkunst()
    program = filmkunst.create_program_db()
    meta = filmkunst.create_meta_db()
    return program, meta


def create_db_schwankhalle():
    print('\n  Working on Schwankhalle')
    schwankhalle = webscraping.Schwankhalle()
    program = schwankhalle.create_program_db()
    return program


def create_database_glocke():
    """ only does the first five things because I'm lazy"""
    print('\n  Working on Glocke')
    glocke = webscraping.Glocke()
    program = glocke.create_program_db()
    return program


def merge_databases(databases):
    database = []
    for x in databases:
        database.extend(x)
    database.sort(key=lambda programinfo: programinfo['datetime'])
    return database


if __name__ == '__main__':
    main()
