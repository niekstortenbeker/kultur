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
    meta_db = quality_control_dbs(program_db, meta_db)

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


def quality_control_dbs(db_programinfo, db_metainfo):
    """so far only check for shows in programinfo but not in metainfo if there is a case mismatch in the title"""
    print('\n\nPerforming a quality control on the metainfo and programinfo databases')
    db_metainfo = find_and_change_case_errors(db_programinfo, db_metainfo, 'Cinema Ostertor')
    db_metainfo = find_and_change_case_errors(db_programinfo, db_metainfo, 'Schauburg')
    db_metainfo = find_and_change_case_errors(db_programinfo, db_metainfo, 'Atlantis')
    db_metainfo = find_and_change_case_errors(db_programinfo, db_metainfo, 'Gondel')
    return db_metainfo


def find_and_change_case_errors(db_programinfo, db_metainfo, location):
    """for the shows in db_programinfo with no entry in db_metainfo, see if these no matches can be resolved when
    ignoring case. If so, change case of the title db_metainfo to reflect the case in db_programinfo"""
    print(f'\n  working on {location}')

    program_titles = set([programinfo['title']
                                   for programinfo in db_programinfo
                                   if programinfo['location'] == location])
    meta_titles = set(db_metainfo[location].keys())
    no_matches = program_titles - meta_titles

    if no_matches:
        matches_after_case_change = []

        for no_match in no_matches:
            for meta_title in meta_titles:
                if no_match.lower() == meta_title.lower():
                    matches_after_case_change.append(no_match)
                    metainfo = db_metainfo[location].pop(meta_title)
                    db_metainfo[location][no_match] = metainfo
                    print(f'    adjusted show title "{meta_title}" to "{no_match}" in db_metainfo')

        no_matches_after_case_change = no_matches - set(matches_after_case_change)

        for title in no_matches_after_case_change:
            print(f'    no meta data found for the show "{title}" in {location}')
    else:
        print("    lookin' good!")
    return db_metainfo


if __name__ == '__main__':
    main()
